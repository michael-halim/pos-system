from msilib.schema import Icon
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox, QSpinBox, QLabel
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QPushButton, QComboBox, QSpinBox, QLabel, QHBoxLayout, QGridLayout, 
    QStackedWidget, QFrame)

import os
from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.getenv("DB_PATH")

class CashierPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cashier App")
        self.setGeometry(100, 100, 400, 300)

        # Central widget setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Product combo box
        self.product_combo = QComboBox()
        self.load_products()
        self.layout.addWidget(self.product_combo)

        # Quantity spin box
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 100)
        self.layout.addWidget(self.quantity_spin)

        # Add to cart button
        self.add_button = QPushButton("Add to Cart")
        self.add_button.clicked.connect(self.add_to_cart)
        self.layout.addWidget(self.add_button)

        # Total label
        self.total_label = QLabel("Total: $0.00")
        self.layout.addWidget(self.total_label)

    def load_products(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM products")
        products = cursor.fetchall()
        conn.close()

        for product in products:
            self.product_combo.addItem(product[1], product[0])

    def add_to_cart(self):
        product_id = self.product_combo.currentData()
        quantity = self.quantity_spin.value()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
        # price = cursor.fetchone()
        # total = price * quantity

        cursor.execute("INSERT INTO transactions (product_id, quantity, total) VALUES (?, ?, ?)",
                       (product_id, quantity, float(12)))
        conn.commit()
        conn.close()

        self.update_total()

    def update_total(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total) FROM transactions")
        total = cursor.fetchone() or 0.0
        conn.close()

        self.total_label.setText(f"Total: ${total}")
