import os
import sqlite3
import smtplib
import secrets
from datetime import datetime, timedelta
from email.message import EmailMessage
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin

from .db import connect

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
login_manager = LoginManager()
login_manager.login_view = "auth.login"

class WebUser(UserMixin):
	def __init__(self, user_row):
		self.id = user_row["id"]
		self.discord_id = user_row["discord_id"]
		self.username = user_row["username"]
		self.password_hash = user_row["password_hash"]

	@staticmethod
	def get_by_id(user_id: int):
		conn = connect()
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
		row = cur.fetchone()
		conn.close()
		return WebUser(row) if row else None

@login_manager.user_loader
def load_user(user_id):
	return WebUser.get_by_id(int(user_id))


def _send_email(to_email: str, subject: str, body: str) -> bool:
	"""Send email using SMTP env config. Returns True if sent, else False."""
	host = os.getenv("SMTP_HOST")
	port = int(os.getenv("SMTP_PORT", "587"))
	user = os.getenv("SMTP_USER")
	pwd = os.getenv("SMTP_PASS")
	from_email = os.getenv("SMTP_FROM", user or "noreply@example.com")
	if not (host and user and pwd and to_email):
		print("Email not configured or missing recipient; printing code instead:\n", body)
		return False
	msg = EmailMessage()
	msg["Subject"] = subject
	msg["From"] = from_email
	msg["To"] = to_email
	msg.set_content(body)
	try:
		with smtplib.SMTP(host, port) as s:
			s.starttls()
			s.login(user, pwd)
			s.send_message(msg)
		return True
	except Exception as e:
		print("Email send failed:", e)
		return False


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		email = request.form.get("email")
		email = email.strip() if email else None
		password = request.form.get("password", "")
		if not username or not password:
			flash("Username and password are required", "error")
			return redirect(url_for("auth.register"))
		conn = connect()
		cur = conn.cursor()
		try:
			cur.execute(
				"INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
				(username, generate_password_hash(password), email),
			)
			conn.commit()
			user_id = cur.lastrowid
		finally:
			conn.close()
		flash("Account created. Please log in.", "success")
		return redirect(url_for("auth.login"))
	return render_template("auth_register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		password = request.form.get("password", "")
		if not username or not password:
			flash("Please enter username and password", "error")
			return redirect(url_for("auth.login"))
		conn = connect()
		cur = conn.cursor()
		cur.execute("SELECT * FROM users WHERE username = ?", (username,))
		row = cur.fetchone()
		if row and row["password_hash"] and check_password_hash(row["password_hash"], password):
			login_user(WebUser(row))
			# Force Roblox verification on onboarding after login
			cur.execute("SELECT is_verified FROM roblox_verification WHERE discord_id = ?", (str(row["id"]),))
			rv = cur.fetchone()
			conn.close()
			if not rv or not bool(rv["is_verified"]):
				return redirect(url_for("profile.verify_roblox"))
			return redirect(url_for("index"))
		conn.close()
		flash("Invalid username or password", "error")
		return redirect(url_for("auth.login"))
	return render_template("auth_login.html")


@auth_bp.route("/forgot", methods=["GET", "POST"])
def forgot_password():
	if request.method == "POST":
		email = request.form.get("email", "").strip()
		if not email:
			flash("Enter your email to receive a reset code", "error")
			return redirect(url_for("auth.forgot_password"))
		code = secrets.token_urlsafe(6)
		expires = datetime.utcnow() + timedelta(minutes=15)
		conn = connect()
		cur = conn.cursor()
		cur.execute("INSERT INTO password_resets (email, code, expires_at) VALUES (?, ?, ?)", (email, code, expires))
		conn.commit()
		conn.close()
		sent = _send_email(email, "AnomiDate Password Reset", f"Your reset code is: {code}\nThis code expires in 15 minutes.")
		if sent:
			flash("Reset code sent to your email", "success")
		else:
			flash("Email not configured; code printed to server logs.", "success")
		return redirect(url_for("auth.reset_password"))
	return render_template("auth_forgot.html")


@auth_bp.route("/reset", methods=["GET", "POST"])
def reset_password():
	if request.method == "POST":
		email = request.form.get("email", "").strip()
		code = request.form.get("code", "").strip()
		new_password = request.form.get("password", "")
		if not (email and code and new_password):
			flash("All fields are required", "error")
			return redirect(url_for("auth.reset_password"))
		conn = connect()
		cur = conn.cursor()
		cur.execute(
			"SELECT id, expires_at, used FROM password_resets WHERE email = ? AND code = ? ORDER BY created_at DESC LIMIT 1",
			(email, code),
		)
		row = cur.fetchone()
		if not row:
			conn.close()
			flash("Invalid code", "error")
			return redirect(url_for("auth.reset_password"))
		try:
			used = bool(row["used"])
			if used:
				flash("Code already used", "error")
				return redirect(url_for("auth.reset_password"))
			cur.execute("UPDATE users SET password_hash = ? WHERE email = ?", (generate_password_hash(new_password), email))
			cur.execute("UPDATE password_resets SET used = TRUE WHERE id = ?", (row["id"],))
			conn.commit()
		finally:
			conn.close()
		flash("Password has been reset. You can now log in.", "success")
		return redirect(url_for("auth.login"))
	return render_template("auth_reset.html")


@auth_bp.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for("index"))
