from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFrame, QLabel, 
    QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
import sqlite3
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")



class MainPage(QWidget):
    login_successful = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Create a form container
        self.form_container = QFrame()
        self.form_container.setMinimumSize(450, 150)
        self.form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(self.form_container)
        
        # Login title
        title = QLabel("Login")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        form_layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # Username field
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin: 5px 0;
            }
        """)
        
        # Password field
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet(self.username.styleSheet())
        
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # Add widgets to form
        form_layout.addWidget(self.username)
        form_layout.addWidget(self.password)
        form_layout.addWidget(self.login_btn)
        form_layout.addStretch()
        
        # Center the form
        self.layout.addStretch()
        self.layout.addWidget(self.form_container, alignment=Qt.AlignCenter)
        self.layout.addStretch()
    
    def check_password(self, password):
        return password == "password"