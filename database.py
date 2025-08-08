# database.py

import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = 'site.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')

    # Create login logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            login_time TEXT NOT NULL
        )
    ''')

    # Insert admin user if not exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone() is None:
        hashed_password = generate_password_hash("Engr.Jude247")
        cursor.execute('''
            INSERT INTO users (username, email, password, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'judykengineeringltd@gmail.com', hashed_password, 1))

    conn.commit()
    conn.close()
