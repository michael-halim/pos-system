from msilib.schema import Icon
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox, QSpinBox, QLabel, QHBoxLayout, QGridLayout, QStackedWidget, QFrame, QLineEdit, QMessageBox
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QPushButton, QComboBox, QSpinBox, QLabel, QHBoxLayout, QGridLayout, 
    QStackedWidget, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal


import pages.cashier as CashierPage
import os
from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.getenv("DB_PATH")

class ModuleButton(QPushButton):
    def __init__(self, title, icon_path=None):
        super().__init__()
        self.setText(title)
        self.setMinimumSize(150, 150)
        if icon_path:
            self.setIcon(Icon(icon_path))
        self.setStyleSheet("""
            QPushButton {
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)


class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout(self)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get active modules and their permissions
        cursor.execute('''
            SELECT 
                m.name,
                m.required_permission_id,
                p.key as permission_key
            FROM modules m
            LEFT JOIN permissions p ON m.required_permission_id = p.permission_id
            WHERE m.is_active = 1
        ''')
        available_modules = cursor.fetchall()
        conn.close()
        
        row = 0
        col = 0
        for module_name, _, permission_key in available_modules:
            if not permission_key or self.parent().check_permission(permission_key):
                btn = ModuleButton(module_name.title(), None)
                self.layout.addWidget(btn, row, col)
                col = (col + 1) % 2
                if col == 0:
                    row += 1