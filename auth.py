# auth.py

from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def create_default_admin():
    users = load_users()
    if "admin" not in users:
        users["admin"] = {
            "password": generate_password_hash("admin123"),
            "access": "admin"
        }
        save_users(users)

def validate_login(username, password):
    users = load_users()
    if username in users and check_password_hash(users[username]["password"], password):
        return True
    return False

def get_user_access(username):
    users = load_users()
    return users.get(username, {}).get("access", "viewer")

def login_required(view_func):
    def wrapper(*args, **kwargs):
        if "username" not in session:
            flash("You must log in first.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def admin_required(view_func):
    def wrapper(*args, **kwargs):
        if session.get("access") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        return view_func(*args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def add_user(username, password, access_level="viewer"):
    users = load_users()
    if username in users:
        return False  # User already exists
    users[username] = {
        "password": generate_password_hash(password),
        "access": access_level
    }
    save_users(users)
    return True

def remove_user(username):
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        return True
    return False

# Initialize admin on first run
create_default_admin()
