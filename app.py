from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# ========== DATABASE MODELS ==========

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
from flask import request, abort
import os

@app.route("/debug-creds")
def debug_creds():
    # Security check using token
    token = request.args.get("token")
    if token != os.environ.get("DEBUG_TOKEN"):
        abort(403)  # Forbidden if token doesn't match

    # Fetch first user from database
    user = User.query.first()
    if user:
        return {
            "username": user.username,
            "password_hash": user.password  # hashed password, not plain text
        }
    else:
        return {"error": "No user found in the database"}
        from werkzeug.security import check_password_hash

@app.route("/check-password")
def check_password():
    token = request.args.get("token")
    if token != os.environ.get("DEBUG_TOKEN"):
        abort(403)

    password_to_test = request.args.get("password")
    if not password_to_test:
        return {"error": "Please provide a password via ?password=yourpassword"}

    user = User.query.first()
    if not user:
        return {"error": "No user found"}

    if check_password_hash(user.password, password_to_test):
        return {"match": True, "message": "Password matches stored hash"}
    else:
        return {"match": False, "message": "Password does NOT match stored hash"}
        from flask import request, abort
import os
from werkzeug.security import generate_password_hash

@app.route("/add-admin")
def add_admin():
    # Check token for security
    token = request.args.get("token")
    if token != os.environ.get("DEBUG_TOKEN"):
        abort(403)  # Forbidden

    # Get username and password from query params
    username = request.args.get("username")
    password = request.args.get("password")

    if not username or not password:
        return {"error": "Username and password are required"}, 400

    # Check if the user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return {"error": "User already exists"}, 400

    # Create new admin user
    new_admin = User(username=username, password=generate_password_hash(password), is_admin=True)
    db.session.add(new_admin)
    db.session.commit()

    return {"success": f"Admin user '{username}' created successfully"}
class Signal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10))
    timeframe = db.Column(db.String(5))
    direction = db.Column(db.String(10))
    time = db.Column(db.String(50))
    approved = db.Column(db.Boolean, default=False)
    @app.route("/debug-creds")
def debug_creds():
    # Check token for security
    token = request.args.get("token")
    if token != os.environ.get("DEBUG_TOKEN"):
        abort(403)  # Forbidden

    # Get the first user in the database
    user = User.query.first()
    if user:
        return {
            "username": user.username,
            "password_hash": user.password  # hashed password, safe to share
        }
    else:
        return {"error": "No user found in the database"}

# ========== INITIAL SETUP ==========

first_request_done = False

@app.before_request
def init_once():
    global first_request_done
    if not first_request_done:
        # Your initialization logic from before_first_request
        try:
            # Example: create database tables
            db.create_all()

            # Example: load your initial signals or setup tasks
            load_signals()

            print("Initialization completed successfully.")
        except Exception as e:
            print(f"Initialization failed: {e}")
        first_request_done = True

# ========== AUTHENTICATION ==========

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('login'))

# ========== DASHBOARD ==========

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    signals = Signal.query.all()
    return render_template('dashboard.html', signals=signals, is_admin=session.get('is_admin', False))

@app.route('/approve/<int:signal_id>')
def approve_signal(signal_id):
    if 'username' not in session or not session.get('is_admin', False):
        return redirect(url_for('login'))
    signal = Signal.query.get(signal_id)
    if signal:
        signal.approved = True
        db.session.commit()
        flash(f"Signal for {signal.symbol} approved and sent!", "success")
        from telegram_sender import send_signal_to_telegram
        send_signal_to_telegram(signal.symbol, signal.direction, signal.timeframe)
    return redirect(url_for('dashboard'))

# ========== USER MANAGEMENT ==========

@app.route('/users')
def manage_users():
    if 'username' not in session or not session.get('is_admin', False):
        return redirect(url_for('login'))
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'username' not in session or not session.get('is_admin', False):
        return redirect(url_for('login'))
    username = request.form['username']
    password = request.form['password']
    existing = User.query.filter_by(username=username).first()
    if existing:
        flash("User already exists", "warning")
    else:
        new_user = User(username=username, password=generate_password_hash(password), is_admin=False)
        db.session.add(new_user)
        db.session.commit()
        flash(f"User '{username}' added.", "success")
    return redirect(url_for('manage_users'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'username' not in session or not session.get('is_admin', False):
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if user and not user.is_admin:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted", "info")
    return redirect(url_for('manage_users'))

# ========== SIGNAL STORAGE ==========

@app.route('/add_signal', methods=['POST'])
def add_signal():
    if request.method == 'POST':
        data = request.json
        new_signal = Signal(
            symbol=data['symbol'],
            timeframe=data['timeframe'],
            direction=data['direction'],
            time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            approved=False
        )
        db.session.add(new_signal)
        db.session.commit()
        return {'status': 'Signal added'}, 200

# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

# ========== RUN APP ==========

if __name__ == '__main__':
    app.run(debug=True)
