from flask import Blueprint, request, redirect, render_template, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

auth_bp = Blueprint('auth', __name__)

USERS_FILE = 'web/users.json'
ADMIN_USERNAME = 'JUDYK'
ADMIN_PASSWORD = 'Engr.Jude247'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            flash('Login successful.', 'success')
            return redirect(url_for('routes.dashboard'))
        else:
            flash('Invalid credentials.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'username' not in session or session['username'] != ADMIN_USERNAME:
        return redirect(url_for('auth.login'))

    users = load_users()

    if request.method == 'POST':
        action = request.form.get('action')
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')

        if action == 'add' and new_username and new_password:
            if new_username in users:
                flash('User already exists.', 'warning')
            else:
                users[new_username] = {
                    'password': generate_password_hash(new_password),
                    'access': 'viewer'
                }
                save_users(users)
                flash(f'User {new_username} added.', 'success')

        elif action == 'remove' and new_username:
            if new_username in users:
                users.pop(new_username)
                save_users(users)
                flash(f'User {new_username} removed.', 'info')
            else:
                flash('User not found.', 'warning')

    return render_template('admin.html', users=users)
