from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # You can keep this key or change it to anything
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Adjust this to your database URI
db = SQLAlchemy(app)

# ========== DATABASE MODELS ==========

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Signal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10))
    timeframe = db.Column(db.String(5))
    direction = db.Column(db.String(10))
    time = db.Column(db.String(50))
    approved = db.Column(db.Boolean, default=False)

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

# ========== DASHBOARD ==========

@app.route('/dashboard')
def dashboard():
    signals = Signal.query.all()
    return render_template('dashboard.html', signals=signals)

@app.route('/approve/<int:signal_id>')
def approve_signal(signal_id):
    signal = Signal.query.get(signal_id)
    if signal:
        signal.approved = True
        db.session.commit()
        flash(f"Signal for {signal.symbol} approved and sent!", "success")
        from telegram_sender import send_signal_to_telegram
        send_signal_to_telegram(signal.symbol, signal.direction, signal.timeframe)
    return redirect(url_for('dashboard'))

# ========== USER MANAGEMENT ==========

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    existing = User.query.filter_by(username=username).first()
    if existing:
        flash("User already exists", "warning")
    else:
        new_user = User(username=username, password=generate_password_hash(password), is_admin=True)  # Admin by default
        db.session.add(new_user)
        db.session.commit()
        flash(f"User '{username}' added.", "success")
    return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted", "info")
    return redirect(url_for('dashboard'))

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

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Empty response to stop favicon errors

# ========== RUN APP ==========

if __name__ == '__main__':
    app.run(debug=True)
