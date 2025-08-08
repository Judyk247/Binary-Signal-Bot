from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from config import ADMIN_USERNAME, ADMIN_PASSWORD, users, admin_email
from telegram_bot import send_telegram_message
import smtplib

routes = Blueprint("routes", __name__)

@routes.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["user"] = username
            flash("Admin logged in successfully!", "success")
            return redirect(url_for("routes.dashboard"))
        elif username in users and users[username] == password:
            session["user"] = username
            flash("Logged in successfully!", "success")
            return redirect(url_for("routes.dashboard"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@routes.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("routes.login"))
    return render_template("dashboard.html")

@routes.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("routes.login"))

@routes.route("/send_signal", methods=["POST"])
def send_signal():
    if "user" not in session:
        return redirect(url_for("routes.login"))
    
    symbol = request.form["symbol"]
    direction = request.form["direction"]
    timeframe = request.form["timeframe"]
    message = f"✅ Signal Approved ✅\nSymbol: {symbol}\nDirection: {direction}\nTimeframe: {timeframe}"
    send_telegram_message(message)
    flash("Signal sent to Telegram!", "success")
    return redirect(url_for("routes.dashboard"))

@routes.route("/admin/add_user", methods=["POST"])
def add_user():
    if "user" not in session or session["user"] != ADMIN_USERNAME:
        flash("Admin access only", "danger")
        return redirect(url_for("routes.dashboard"))
    
    new_username = request.form["new_username"]
    new_password = request.form["new_password"]
    if new_username in users:
        flash("User already exists", "warning")
    else:
        users[new_username] = new_password
        flash(f"User {new_username} added successfully!", "success")
    return redirect(url_for("routes.dashboard"))

@routes.route("/admin/remove_user", methods=["POST"])
def remove_user():
    if "user" not in session or session["user"] != ADMIN_USERNAME:
        flash("Admin access only", "danger")
        return redirect(url_for("routes.dashboard"))
    
    remove_username = request.form["remove_username"]
    if remove_username in users:
        del users[remove_username]
        flash(f"User {remove_username} removed successfully!", "success")
    else:
        flash("User not found", "warning")
    return redirect(url_for("routes.dashboard"))
