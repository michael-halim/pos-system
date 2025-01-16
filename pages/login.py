from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFrame, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
import sqlite3
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")



class LoginPage(QWidget):
    login_successful = pyqtSignal(str, str)  # Signal to emit username and role
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        # Create a form container
        self.form_container = QFrame()
        self.form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(self.form_container)
        
        # Add title
        title = QLabel("Login")
        title.setStyleSheet("font-size: 24px; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                margin-bottom: 10px;
            }
        """)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                margin-bottom: 10px;
            }
        """)
        
        # Create button container
        button_container = QHBoxLayout()
        
        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.login_btn.clicked.connect(self.check_credentials)
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.close_btn.clicked.connect(self.close_application)
        
        # Add buttons to container
        button_container.addWidget(self.login_btn)
        button_container.addWidget(self.close_btn)
        
        # Add widgets to form
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addLayout(button_container)
        form_layout.addStretch()
        
        # Center the form
        self.layout.addStretch()
        self.layout.addWidget(self.form_container, alignment=Qt.AlignCenter)
        self.layout.addStretch()
        
        # Set fixed size for form container
        self.form_container.setFixedWidth(300)
    
    def clear_inputs(self):
        self.username_input.clear()
        self.password_input.clear()
    
    def check_credentials(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return False
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            # Get user data including role
            cursor.execute('''
                SELECT u.password_hash, u.user_id, r.name as role_name 
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                WHERE u.username = ? AND u.is_active = 1
            ''', (username,))
            
            user_data = cursor.fetchone()
            
            if user_data:
                stored_hash = user_data[0]
                
                # Check password using bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    self.login_successful.emit(username, user_data[2])  # Emit username and role
                    self.clear_inputs()
                    return True
                else:
                    QMessageBox.warning(self, "Error", "Invalid credentials")
                    return False
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials")
                return False
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
            return False
        finally:
            conn.close()
    
    def close_application(self):
        reply = QMessageBox.question(self, 'Close Application', 
                                   'Are you sure you want to close the application?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            QApplication.quit()