from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required
from .db import connect

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ADMIN_PASSWORD = "MINDBL0Wn!.."


def _is_admin():
	return session.get("is_admin") is True


@admin_bp.before_app_request
def protect_admin():
	# Only lock down /admin paths
	from flask import request
	if request.path.startswith("/admin"):
		if request.path != "/admin/login" and not _is_admin():
			return redirect(url_for("admin.login"))


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		pwd = request.form.get("password", "")
		if pwd == ADMIN_PASSWORD:
			session["is_admin"] = True
			flash("Admin login successful", "success")
			return redirect(url_for("admin.dashboard"))
		flash("Invalid admin password", "error")
		return redirect(url_for("admin.login"))
	return render_template("admin_login.html")


@admin_bp.route("/logout")
def logout():
	session.pop("is_admin", None)
	flash("Logged out", "success")
	return redirect(url_for("admin.login"))


@admin_bp.route("/")
@admin_bp.route("/dashboard")
def dashboard():
	if not _is_admin():
		return redirect(url_for("admin.login"))
	# Simple stats
	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT COUNT(*) AS c FROM users")
	row = cur.fetchone()
	total_users = row["c"] if row else 0
	cur.execute("SELECT COUNT(*) AS c FROM mutual_matches")
	row = cur.fetchone()
	total_matches = row["c"] if row else 0
	cur.execute("SELECT COUNT(*) AS c FROM messages")
	row = cur.fetchone()
	total_msgs = row["c"] if row else 0
	conn.close()
	return render_template("admin_dashboard.html", total_users=total_users, total_matches=total_matches, total_msgs=total_msgs)
