from msilib.schema import Icon
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox, QSpinBox, QLabel, QHBoxLayout, QGridLayout, QStackedWidget, QFrame, QLineEdit, QMessageBox
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QPushButton, QComboBox, QSpinBox, QLabel, QHBoxLayout, QGridLayout, 
    QStackedWidget, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal

import os
from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.getenv("DB_PATH")

class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setMaximumWidth(200)
        self.setStyleSheet("background-color: #f0f0f0;")
        
        # Add sidebar buttons
        self.buttons = []
        modules = ["Home", "Cashier", "Inventory", "Reports", "Settings"]
        for module in modules:
            btn = QPushButton(module)
            self.buttons.append(btn)
            self.layout.addWidget(btn)
        
        self.layout.addStretch()