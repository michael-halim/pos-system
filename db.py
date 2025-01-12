import sqlite3

def setup_database(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables for products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    # Create tables for transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # Create roles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    ''')

    # Create permissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    ''')

    # Create role_permissions table (many-to-many relationship)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INTEGER,
            permission_id INTEGER,
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (permission_id) REFERENCES permissions(id),
            PRIMARY KEY (role_id, permission_id)
        )
    ''')

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role_id INTEGER,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
    ''')

    # Insert default roles
    cursor.execute('''
        INSERT OR IGNORE INTO roles (name, description) VALUES 
        ('admin', 'Full system access'),
        ('manager', 'Store management access'),
        ('cashier', 'Basic cashier access')
    ''')

    # Insert default permissions
    cursor.execute('''
        INSERT OR IGNORE INTO permissions (name, description) VALUES 
        ('user_manage', 'Can manage users'),
        ('inventory_manage', 'Can manage inventory'),
        ('sales_view', 'Can view sales reports'),
        ('sales_create', 'Can create sales'),
        ('settings_manage', 'Can manage settings')
    ''')

     # Create modules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            is_active BOOLEAN DEFAULT 1,
            required_permission_id INTEGER,
            FOREIGN KEY (required_permission_id) REFERENCES permissions(id)
        )
    ''')

    # Insert default modules
    cursor.execute('''
        INSERT OR IGNORE INTO modules (name, required_permission_id) VALUES 
        ('home', NULL),
        ('cashier', (SELECT id FROM permissions WHERE name = 'sales_create')),
        ('inventory', (SELECT id FROM permissions WHERE name = 'inventory_manage')),
        ('reports', (SELECT id FROM permissions WHERE name = 'sales_view')),
        ('settings', (SELECT id FROM permissions WHERE name = 'settings_manage'))
    ''')

     # Add default admin user if it doesn't exist
    # admin_password = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt())
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, role_id, is_active)
        VALUES (?, ?, (SELECT id FROM roles WHERE name = 'admin'), 1)
    ''', ('admin', 'password'))


     # Assign default permissions to roles
    admin_permissions = ['user_manage', 'inventory_manage', 'sales_view', 'sales_create', 'settings_manage']
    manager_permissions = ['inventory_manage', 'sales_view', 'sales_create']
    cashier_permissions = ['sales_create', 'sales_view']

     # Helper function to assign permissions
    def assign_role_permissions(role_name, permission_names):
        cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
        role_id = cursor.fetchone()[0]
        
        for perm_name in permission_names:
            cursor.execute('SELECT id FROM permissions WHERE name = ?', (perm_name,))
            perm_id = cursor.fetchone()[0]
            cursor.execute('INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)',
                         (role_id, perm_id))

    assign_role_permissions('admin', admin_permissions)
    assign_role_permissions('manager', manager_permissions)
    assign_role_permissions('cashier', cashier_permissions)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database("cashier.db")
