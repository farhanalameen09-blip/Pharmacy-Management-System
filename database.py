import sqlite3
import os
import hashlib

from contextlib import contextmanager
from config import DATABASE_PATH, DATABASE_DIR


# ==========================================
# DATABASE CONNECTION
# ==========================================

@contextmanager
def get_connection():
    """Provide a managed SQLite database connection."""

    os.makedirs(DATABASE_DIR, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


# ==========================================
# CREATE TABLES
# ==========================================

def create_tables():

    with get_connection() as connection:
        cursor = connection.cursor()

        # USERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)

        # SUPPLIERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        """)

        # MEDICINES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                manufacturer TEXT,
                batch_no TEXT UNIQUE NOT NULL,
                purchase_price REAL NOT NULL,
                selling_price REAL NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                min_stock INTEGER NOT NULL DEFAULT 10,
                expiry_date TEXT NOT NULL,
                supplier_id INTEGER,
                description TEXT
            )
        """)

        # CUSTOMERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        """)

        # SALES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE NOT NULL,
                customer_id INTEGER,
                user_id INTEGER,
                sale_date TEXT NOT NULL,
                subtotal REAL NOT NULL,
                discount REAL DEFAULT 0,
                tax REAL DEFAULT 0,
                total REAL NOT NULL
            )
        """)

        # SALE ITEMS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total REAL NOT NULL
            )
        """)

        # SETTINGS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                theme TEXT DEFAULT 'light'
            )
        """)

        # FEEDBACK
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ease_of_use INTEGER,
                dashboard_usefulness INTEGER,
                report_clarity INTEGER,
                navigation INTEGER,
                shortcut_usefulness INTEGER,
                overall_satisfaction INTEGER,
                comments TEXT,
                feedback_date TEXT NOT NULL
            )
        """)

    print("Database tables created successfully.")


# ==========================================
# DEFAULT ADMIN
# ==========================================

def create_default_admin():

    username = "admin"
    password = "admin123"
    role = "Admin"

    hashed_password = hashlib.sha256(
        password.encode()
    ).hexdigest()

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO users
            (username, password, role)
            VALUES (?, ?, ?)
        """, (username, hashed_password, role))

    print("Default admin account ready.")


# ==========================================
# RUN DATABASE
# ==========================================

if __name__ == "__main__":
    create_tables()
    create_default_admin()