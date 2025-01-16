import sqlite3
import bcrypt

def setup_database(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop all existing tables first
    cursor.execute("DROP TABLE IF EXISTS role_permissions")
    cursor.execute("DROP TABLE IF EXISTS modules")
    cursor.execute("DROP TABLE IF EXISTS permissions")
    cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS roles")
    cursor.execute("DROP TABLE IF EXISTS products")

    # Create tables for products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    # Create tables for transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')

    # Create roles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            role_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE CHECK(length(name) <= 20),
            description TEXT CHECK(length(description) <= 60)
        )
    ''')

    # Create permissions table with module-specific permissions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            permission_id INTEGER PRIMARY KEY,
            key TEXT NOT NULL UNIQUE
        )
    ''')

    # Create role_permissions table (many-to-many relationship)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INTEGER,
            permission_id INTEGER,
            FOREIGN KEY (role_id) REFERENCES roles(role_id),
            FOREIGN KEY (permission_id) REFERENCES permissions(permission_id),
            PRIMARY KEY (role_id, permission_id)
        )
    ''')

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(role_id)
        )
    ''')

    # Create modules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS modules (
            module_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            is_active BOOLEAN DEFAULT 1,
            required_permission_id INTEGER,
            FOREIGN KEY (required_permission_id) REFERENCES permissions(permission_id)
        )
    ''')

    # Insert default roles
    cursor.execute('''
        INSERT INTO roles (name, description) VALUES 
        ('admin', 'Full system access'),
        ('manager', 'Store management access'),
        ('cashier', 'Basic cashier access')
    ''')

    # Insert default permissions with module-specific actions
    cursor.execute('''
        INSERT INTO permissions (key) VALUES 
        ('users_read'),
        ('users_write'),
        ('users_update'),
        ('users_delete'),
        ('inventory_read'),
        ('inventory_write'),
        ('inventory_update'),
        ('inventory_delete'),
        ('sales_read'),
        ('sales_write'),
        ('sales_update'),
        ('sales_delete'),
        ('reports_read'),
        ('settings_read'),
        ('settings_write'),
        ('settings_update'),
        ('settings_delete')
    ''')

    # Insert default modules
    cursor.execute('''
        INSERT INTO modules (name, is_active) VALUES 
        ('home', 1),
        ('cashier', 1),
        ('inventory', 1),
        ('reports', 1),
        ('settings', 1)
    ''')

    # Add default admin user with bcrypt hashed password
    default_password = 'admin123'  # You should change this in production
    password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
    
    cursor.execute('''
        INSERT INTO users (username, password_hash, role_id, is_active)
        VALUES (?, ?, (SELECT role_id FROM roles WHERE name = 'admin'), 1)
    ''', ('admin', password_hash))

    # Define permission assignments for each role
    admin_permissions = [
        'users_read', 'users_write', 'users_update', 'users_delete',
        'inventory_read', 'inventory_write', 'inventory_update', 'inventory_delete',
        'sales_read', 'sales_write', 'sales_update', 'sales_delete',
        'reports_read',
        'settings_read', 'settings_write', 'settings_update', 'settings_delete'
    ]
    
    manager_permissions = [
        'inventory_read', 'inventory_write', 'inventory_update',
        'sales_read', 'sales_write', 'sales_update',
        'reports_read'
    ]
    
    cashier_permissions = [
        'sales_read', 'sales_write'
    ]

    def assign_role_permissions(role_name, permission_keys):
        cursor.execute('SELECT role_id FROM roles WHERE name = ?', (role_name,))
        role_id = cursor.fetchone()[0]
        
        for perm_key in permission_keys:
            cursor.execute('SELECT permission_id FROM permissions WHERE key = ?', (perm_key,))
            perm_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)',
                         (role_id, perm_id))

    assign_role_permissions('admin', admin_permissions)
    assign_role_permissions('manager', manager_permissions)
    assign_role_permissions('cashier', cashier_permissions)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database("cashier.db")
