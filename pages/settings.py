from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QDialog, 
    QFormLayout, QLineEdit, QLabel, QTabWidget, QCheckBox)
from PyQt5.QtCore import Qt
import sqlite3
import bcrypt
import os

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.tab_widget.addTab(UsersTab(), "Users")
        self.tab_widget.addTab(RolesTab(), "Roles")
        self.tab_widget.addTab(PermissionsTab(), "Permissions")
        self.tab_widget.addTab(ModulesTab(), "Modules")
        
        self.layout.addWidget(self.tab_widget)

class UsersTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        add_btn = QPushButton("Add User")
        add_btn.clicked.connect(self.add_user)
        toolbar.addWidget(add_btn)
        toolbar.addStretch()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Username", "Role", "Status", "Created At", "Actions"])
        
        layout.addLayout(toolbar)
        layout.addWidget(self.table)
        
        self.load_users()
    
    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()  # Refresh the table
    
    def load_users(self):
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT users.username, roles.name, users.is_active, users.created_at 
            FROM users 
            JOIN roles ON users.role_id = roles.role_id
        ''')
        users = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(users))
        for i, user in enumerate(users):
            for j, value in enumerate(user):
                item = QTableWidgetItem(str(value))
                if j == 2:  # Status column
                    item.setText("Active" if value else "Inactive")
                self.table.setItem(i, j, item)
            
            # Add action buttons
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, row=i: self.edit_user(row))
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, row=i: self.delete_user(row))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            self.table.setCellWidget(i, 4, actions)

    def edit_user(self, row):
        username = self.table.item(row, 0).text()
        dialog = EditUserDialog(username, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()  # Refresh the table

    def delete_user(self, row):
        username = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, 'Delete User', 
                                   f'Are you sure you want to delete user {username}?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(os.getenv("DB_PATH"))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            self.load_users()  # Refresh the table


class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add User")
        self.layout = QFormLayout(self)
        
        # Create form fields
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        
        self.role_combo = QComboBox()
        self.load_roles()
        
        # Add fields to form
        self.layout.addRow("Username:", self.username)
        self.layout.addRow("Password:", self.password)
        self.layout.addRow("Role:", self.role_combo)
        
        # Add buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_user)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        self.layout.addRow(button_box)

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


class EditUserDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle(f"Edit User: {username}")
        self.layout = QFormLayout(self)
        
        # Create form fields
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Leave blank to keep current password")
        
        self.role_combo = QComboBox()
        self.load_roles()
        self.load_user_data()
        
        # Add fields to form
        self.layout.addRow("New Password:", self.password)
        self.layout.addRow("Role:", self.role_combo)
        
        # Add buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        self.layout.addRow(button_box)

    def load_roles(self):
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM roles")
        roles = cursor.fetchall()
        conn.close()
        
        for role_id, role_name in roles:
            self.role_combo.addItem(role_name, role_id)

    def load_user_data(self):
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        cursor.execute("SELECT role_id FROM users WHERE username = ?", (self.username,))
        role_id = cursor.fetchone()[0]
        conn.close()
        
        # Set current role in combo box
        index = self.role_combo.findData(role_id)
        if index >= 0:
            self.role_combo.setCurrentIndex(index)

    def save_changes(self):
        new_password = self.password.text()
        role_id = self.role_combo.currentData()
        
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        
        try:
            if new_password:
                # Update password and role
                password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute(
                    "UPDATE users SET password_hash = ?, role_id = ? WHERE username = ?",
                    (password_hash, role_id, self.username)
                )
            else:
                # Update role only
                cursor.execute(
                    "UPDATE users SET role_id = ? WHERE username = ?",
                    (role_id, self.username)
                )
            
            conn.commit()
            self.accept()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to update user: {str(e)}")
        finally:
            conn.close()

class RolesTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        add_btn = QPushButton("Add Role")
        add_btn.clicked.connect(self.add_role)
        toolbar.addWidget(add_btn)
        toolbar.addStretch()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Description", "Permissions", "Actions"])
        
        layout.addLayout(toolbar)
        layout.addWidget(self.table)
        
        self.load_roles()

    def add_role(self):
        dialog = AddRoleDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_roles()

    def load_roles(self):
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        
        # Get roles with their permissions
        cursor.execute('''
            SELECT r.role_id, r.name, r.description,
                   GROUP_CONCAT(p.key) as permissions
            FROM roles r
            LEFT JOIN role_permissions rp ON r.role_id = rp.role_id
            LEFT JOIN permissions p ON rp.permission_id = p.permission_id
            GROUP BY r.role_id
        ''')
        roles = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(roles))
        for i, (role_id, key, description, permissions) in enumerate(roles):
            self.table.setItem(i, 0, QTableWidgetItem(key))
            self.table.setItem(i, 1, QTableWidgetItem(description or ""))
            self.table.setItem(i, 2, QTableWidgetItem(permissions or ""))
            
            # Add action buttons
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, r=role_id: self.edit_role(r))
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, r=role_id: self.delete_role(r))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            self.table.setCellWidget(i, 3, actions)

    def edit_role(self, role_id):
        dialog = EditRoleDialog(role_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_roles()

    def delete_role(self, role_id):
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        
        # Get role name
        cursor.execute("SELECT name FROM roles WHERE id = ?", (role_id,))
        role_name = cursor.fetchone()[0]
        
        # Check if role has users
        cursor.execute("SELECT COUNT(*) FROM users WHERE role_id = ?", (role_id,))
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            QMessageBox.warning(self, "Cannot Delete Role", 
                              f"Role '{role_name}' is assigned to {user_count} users. "
                              "Please reassign these users before deleting the role.")
            return
        
        reply = QMessageBox.question(self, 'Delete Role', 
                                   f'Are you sure you want to delete role "{role_name}"?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Delete role permissions first
                cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (role_id,))
                # Then delete the role
                cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
                conn.commit()
                self.load_roles()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"Failed to delete role: {str(e)}")
            finally:
                conn.close()


class AddRoleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Role")
        self.layout = QVBoxLayout(self)
        
        # Create form
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        
        # Permissions group
        permissions_group = QWidget()
        permissions_layout = QVBoxLayout(permissions_group)
        permissions_layout.addWidget(QLabel("Permissions:"))
        
        # Load permissions checkboxes
        self.permission_boxes = {}
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM permissions")
        for perm_id, name, description in cursor.fetchall():
            checkbox = QCheckBox(f"{name} - {description}")
            self.permission_boxes[perm_id] = checkbox
            permissions_layout.addWidget(checkbox)
        conn.close()
        
        # Add layouts to main layout
        self.layout.addLayout(form_layout)
        self.layout.addWidget(permissions_group)
        
        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_role)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        self.layout.addLayout(buttons)

    def save_role(self):
        name = self.name_input.text()
        description = self.description_input.text()
        
        if not name:
            QMessageBox.warning(self, "Error", "Role name is required")
            return
        
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        
        try:
            # Insert role
            cursor.execute(
                "INSERT INTO roles (name, description) VALUES (?, ?)",
                (name, description)
            )
            role_id = cursor.lastrowid
            
            # Insert permissions
            for perm_id, checkbox in self.permission_boxes.items():
                if checkbox.isChecked():
                    cursor.execute(
                        "INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
                        (role_id, perm_id)
                    )
            
            conn.commit()
            self.accept()
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Role name already exists")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to create role: {str(e)}")
        finally:
            conn.close()


class EditRoleDialog(QDialog):
    def __init__(self, role_id, parent=None):
        super().__init__(parent)
        self.role_id = role_id
        self.setWindowTitle("Edit Role")
        self.layout = QVBoxLayout(self)
        
        # Create form
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        
        # Permissions group
        permissions_group = QWidget()
        permissions_layout = QVBoxLayout(permissions_group)
        permissions_layout.addWidget(QLabel("Permissions:"))
        
        # Load permissions checkboxes
        self.permission_boxes = {}
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        
        # Load current role data
        cursor.execute("SELECT name, description FROM roles WHERE id = ?", (role_id,))
        role_name, role_description = cursor.fetchone()
        self.name_input.setText(role_name)
        self.description_input.setText(role_description or "")
        
        # Load permissions and check current ones
        cursor.execute("SELECT id, name, description FROM permissions")
        permissions = cursor.fetchall()
        
        cursor.execute("SELECT permission_id FROM role_permissions WHERE role_id = ?", (role_id,))
        current_permissions = {row[0] for row in cursor.fetchall()}
        
        for perm_id, name, description in permissions:
            checkbox = QCheckBox(f"{name} - {description}")
            checkbox.setChecked(perm_id in current_permissions)
            self.permission_boxes[perm_id] = checkbox
            permissions_layout.addWidget(checkbox)
            
        conn.close()
        
        # Add layouts to main layout
        self.layout.addLayout(form_layout)
        self.layout.addWidget(permissions_group)
        
        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        self.layout.addLayout(buttons)

    def save_changes(self):
        name = self.name_input.text()
        description = self.description_input.text()
        
        if not name:
            QMessageBox.warning(self, "Error", "Role name is required")
            return
        
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        
        try:
            # Update role
            cursor.execute(
                "UPDATE roles SET name = ?, description = ? WHERE id = ?",
                (name, description, self.role_id)
            )
            
            # Update permissions
            cursor.execute("DELETE FROM role_permissions WHERE role_id = ?", (self.role_id,))
            for perm_id, checkbox in self.permission_boxes.items():
                if checkbox.isChecked():
                    cursor.execute(
                        "INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
                        (self.role_id, perm_id)
                    )
            
            conn.commit()
            self.accept()
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Role name already exists")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to update role: {str(e)}")
        finally:
            conn.close()

class PermissionsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        add_btn = QPushButton("Add Permission")
        add_btn.clicked.connect(self.add_permission)
        toolbar.addWidget(add_btn)
        toolbar.addStretch()
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Description", "Assigned To", "Actions"])
        
        layout.addLayout(toolbar)
        layout.addWidget(self.table)
        
        self.load_permissions()

    def load_permissions(self):
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                p.permission_id,
                p.key,
                GROUP_CONCAT(r.name) as roles
            FROM permissions p
            LEFT JOIN role_permissions rp ON p.permission_id = rp.permission_id
            LEFT JOIN roles r ON rp.role_id = r.role_id
            GROUP BY p.permission_id
        ''')
        permissions = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(permissions))
        for i, (perm_id, key, roles) in enumerate(permissions):
            self.table.setItem(i, 0, QTableWidgetItem(key))
            self.table.setItem(i, 1, QTableWidgetItem(roles or ""))
            
            # Add action buttons
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, p=perm_id: self.edit_permission(p))
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, p=perm_id: self.delete_permission(p))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            self.table.setCellWidget(i, 3, actions)

    def add_permission(self):
        dialog = AddPermissionDialog(self)
        if dialog.exec_() == QDialog.Accepted:   
            self.load_permissions()

    def edit_permission(self, perm_id):
        dialog = EditPermissionDialog(perm_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_permissions()

    def delete_permission(self, perm_id):
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        
        # Get permission name
        cursor.execute("SELECT name FROM permissions WHERE id = ?", (perm_id,))
        perm_name = cursor.fetchone()[0]
        
        # Check if permission is assigned to any roles
        cursor.execute("SELECT COUNT(*) FROM role_permissions WHERE permission_id = ?", (perm_id,))
        role_count = cursor.fetchone()[0]
        
        if role_count > 0:
            QMessageBox.warning(self, "Cannot Delete Permission", 
                              f"Permission '{perm_name}' is assigned to {role_count} roles. "
                              "Please remove these assignments before deleting the permission.")
            return
        
        reply = QMessageBox.question(self, 'Delete Permission', 
                                   f'Are you sure you want to delete permission "{perm_name}"?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                cursor.execute("DELETE FROM permissions WHERE id = ?", (perm_id,))
                conn.commit()
                self.load_permissions()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"Failed to delete permission: {str(e)}")
            finally:
                conn.close()

class ModulesTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Status", "Required Permission", "Actions"])
        
        layout.addWidget(self.table)
        
        self.load_modules()

    def load_modules(self):
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        
        # Get modules with their required permissions
        cursor.execute('''
            SELECT 
                m.module_id,
                m.name,
                m.is_active,
                p.key as permission_key
            FROM modules m
            LEFT JOIN permissions p ON m.required_permission_id = p.permission_id
        ''')
        modules = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(modules))
        for i, (module_id, name, is_active, permission_key) in enumerate(modules):
            # Module name
            self.table.setItem(i, 0, QTableWidgetItem(name))
            
            # Status
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_checkbox = QCheckBox()
            status_checkbox.setChecked(bool(is_active))
            status_checkbox.stateChanged.connect(lambda state, mid=module_id: self.toggle_module(mid, state))
            status_layout.addWidget(status_checkbox)
            status_layout.setAlignment(Qt.AlignCenter)
            status_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(i, 1, status_widget)
            
            # Required permission
            self.table.setItem(i, 2, QTableWidgetItem(permission_key or "None"))
            
            # Actions
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, m=module_id: self.edit_module(m))
            actions_layout.addWidget(edit_btn)
            
            self.table.setCellWidget(i, 3, actions)
            
            # Make name and permission cells read-only
            for col in [0, 2]:
                item = self.table.item(i, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def toggle_module(self, module_id, state):
        """Toggle module active status"""
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE modules SET is_active = ? WHERE id = ?",
                (bool(state), module_id)
            )
            conn.commit()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to update module status: {str(e)}")
        finally:
            conn.close()

    def edit_module(self, module_id):
        dialog = EditModuleDialog(module_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_modules()


class EditModuleDialog(QDialog):
    def __init__(self, module_id, parent=None):
        super().__init__(parent)
        self.module_id = module_id
        self.setWindowTitle("Edit Module")
        self.layout = QVBoxLayout(self)
        
        # Create form
        form_layout = QFormLayout()
        
        # Required permission combo
        self.permission_combo = QComboBox()
        self.permission_combo.addItem("None", None)
        
        # Load permissions
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name FROM permissions")
        for perm_id, name in cursor.fetchall():
            self.permission_combo.addItem(name, perm_id)
        
        # Load current module data
        cursor.execute("""
            SELECT name, required_permission_id 
            FROM modules 
            WHERE id = ?
        """, (module_id,))
        module_name, current_permission_id = cursor.fetchone()
        conn.close()
        
        # Set current values
        self.name_label = QLabel(module_name)
        if current_permission_id:
            index = self.permission_combo.findData(current_permission_id)
            if index >= 0:
                self.permission_combo.setCurrentIndex(index)
        
        form_layout.addRow("Name:", self.name_label)
        form_layout.addRow("Required Permission:", self.permission_combo)
        
        self.layout.addLayout(form_layout)
        
        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_changes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        self.layout.addLayout(buttons)

    def save_changes(self):
        permission_id = self.permission_combo.currentData()
        
        conn = sqlite3.connect(os.getenv("DB_PATH"))
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE modules SET required_permission_id = ? WHERE module_id = ?",
                (permission_id, self.module_id)
            )
            conn.commit()
            self.accept()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to update module: {str(e)}")
        finally:
            conn.close()
