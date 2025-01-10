from msilib.schema import Icon
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox, QSpinBox, QLabel, QHBoxLayout, QGridLayout, QStackedWidget, QFrame, QLineEdit, QMessageBox
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QPushButton, QComboBox, QSpinBox, QLabel, QHBoxLayout, QGridLayout, 
    QStackedWidget, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal

import widgets.sidebar as Sidebar
import pages.login as Login
import pages.home as Home
import pages.cashier as Cashier
import os
from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.getenv("DB_PATH")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cashier App")
        self.showFullScreen()
        
        # Create stacked widget for login and main content
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)
        
        # Create login page
        self.login_page = Login.MainPage()
        self.login_page.login_successful.connect(self.on_login_success)
        self.central_stack.addWidget(self.login_page)
        
        # Create main content widget
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)
        self.central_stack.addWidget(self.main_widget)

        # Create sidebar
        self.sidebar = Sidebar.Sidebar()
        self.main_layout.addWidget(self.sidebar)

        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Add pages
        self.stacked_widget.addWidget(Cashier.CashierPage())
        self.stacked_widget.addWidget(Home.MainPage())

        # Connect sidebar buttons
        self.sidebar.buttons[0].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.sidebar.buttons[1].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        # Add logout button to sidebar
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.sidebar.layout.addWidget(self.logout_btn)
        
        # Connect login/logout signals
        self.login_page.login_btn.clicked.connect(self.handle_login)
        self.logout_btn.clicked.connect(self.handle_logout)
        
        # Start with login page
        self.central_stack.setCurrentIndex(0)
    
    def on_login_success(self):
        """Handle successful login"""
        self.central_stack.setCurrentIndex(1)
    
    def handle_login(self):
        username = self.login_page.username.text()
        password = self.login_page.password.text()
        if username == "admin" and password == "password":
            self.central_stack.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")


    def handle_logout(self):
        reply = QMessageBox.question(self, 'Logout', 'Are you sure you want to logout?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.central_stack.setCurrentIndex(0)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())