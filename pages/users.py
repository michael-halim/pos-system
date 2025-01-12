from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QDialog, 
    QFormLayout, QLineEdit, QLabel)
from PyQt5.QtCore import Qt
import sqlite3
import bcrypt
import os

class UserManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # Create toolbar
        toolbar = QHBoxLayout()
        self.add_user_btn = QPushButton("Add User")
        self.add_user_btn.clicked.connect(self.show_add_user_dialog)
        toolbar.addWidget(self.add_user_btn)
        toolbar.addStretch()
        
        # Create user table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["Username", "Role", "Status", "Actions"])
        
        self.layout.addLayout(toolbar)
        self.layout.addWidget(self.user_table)
        
        self.load_users()

    def load_users(self):
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT users.username, roles.name, users.is_active, users.id 
            FROM users 
            JOIN roles ON users.role_id = roles.id
        ''')
        users = cursor.fetchall()
        conn.close()

        self.user_table.setRowCount(len(users))
        for i, user in enumerate(users):
            self.user_table.setItem(i, 0, QTableWidgetItem(user[0]))
            self.user_table.setItem(i, 1, QTableWidgetItem(user[1]))
            self.user_table.setItem(i, 2, QTableWidgetItem("Active" if user[2] else "Inactive"))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, u=user: self.show_edit_user_dialog(u))
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, u=user: self.delete_user(u[3]))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            self.user_table.setCellWidget(i, 3, actions_widget)

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add User")
        self.layout = QFormLayout(self)
        
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        
        self.role_combo = QComboBox()
        self.load_roles()
        
        self.layout.addRow("Username:", self.username)
        self.layout.addRow("Password:", self.password)
        self.layout.addRow("Role:", self.role_combo)
        
        buttons = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_user)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.cancel_btn)
        self.layout.addRow(buttons)

    def load_roles(self):
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM roles")
        roles = cursor.fetchall()
        conn.close()
        
        for role_id, role_name in roles:
            self.role_combo.addItem(role_name, role_id)

    def save_user(self):
        username = self.username.text()
        password = self.password.text()
        role_id = self.role_combo.currentData()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role_id) VALUES (?, ?, ?)",
                (username, password_hash, role_id)
            )
            conn.commit()
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username already exists")
        finally:
            conn.close()
