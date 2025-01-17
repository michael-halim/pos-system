from msilib.schema import Icon
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox, QSpinBox, QLabel, QHBoxLayout, QGridLayout, QStackedWidget, QFrame, QLineEdit, QMessageBox
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QPushButton, QComboBox, QSpinBox, QLabel, QHBoxLayout, QGridLayout, 
    QStackedWidget, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
import bcrypt

import widgets.sidebar as Sidebar
import pages.login as Login
import pages.home as Home
import pages.cashier as Cashier
import pages.settings as Settings
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
        self.login_page = Login.LoginPage()
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

        # Create pages dictionary to store pages and their indices
        self.pages = {
            'home': Home.MainPage(),
            'cashier': Cashier.CashierPage(),
            'settings': Settings.SettingsPage()
        }

        # Add pages to stacked widget and store their indices
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)

        # Connect sidebar buttons with named routes
        self.sidebar.buttons['home'].clicked.connect(lambda: self.navigate_to('home'))
        self.sidebar.buttons['cashier'].clicked.connect(lambda: self.navigate_to('cashier'))
        self.sidebar.buttons['settings'].clicked.connect(lambda: self.navigate_to('settings'))
        
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
        if self.login_page.check_credentials():
            self.central_stack.setCurrentIndex(1)

    def handle_logout(self):
        reply = QMessageBox.question(self, 'Logout', 'Are you sure you want to logout?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.central_stack.setCurrentIndex(0)

    def navigate_to(self, route_name):
        """Navigate to a specific page by route name"""
        if route_name == 'settings' and not self.check_permission('settings_manage'):
            QMessageBox.warning(self, "Access Denied", "You don't have permission to access this page")
            return
        
        page = self.pages.get(route_name)
        if page:
            self.stacked_widget.setCurrentWidget(page)

    def check_permission(self, permission_name):
        """Check if current user has specific permission"""
        # conn = sqlite3.connect(DB_PATH)
        # cursor = conn.cursor()
        # cursor.execute('''
        #     SELECT COUNT(*) FROM users u
        #     JOIN role_permissions rp ON u.role_id = rp.role_id
        #     JOIN permissions p ON rp.permission_id = p.permission_id
        #     WHERE u.username = ? AND p.key = ?
        # ''', (self.current_user, permission_name))
        # has_permission = cursor.fetchone()[0] > 0
        # conn.close()
        return True


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())