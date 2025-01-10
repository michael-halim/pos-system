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
        
        # Create module buttons
        modules = [
            ("Cashier", None),
            ("Inventory", None),
            ("Reports", None),
            ("Settings", None)
        ]
        
        for i, (title, icon) in enumerate(modules):
            btn = ModuleButton(title, icon)
            row = i // 2
            col = i % 2
            self.layout.addWidget(btn, row, col)