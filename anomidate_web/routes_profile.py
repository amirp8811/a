from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import json
from .db import connect
from .roblox import resolve_roblox_username, check_roblox_verification, get_avatar_url

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/view")
@login_required
def view_profile():
	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE id = ?", (current_user.id,))
	user = cur.fetchone()
	cur.execute("SELECT * FROM roblox_verification WHERE discord_id = ?", (str(current_user.id),))
	rv = cur.fetchone()
	conn.close()
	server_prefs = []
	if user and user["server_preferences"]:
		try:
			server_prefs = json.loads(user["server_preferences"]) or []
		except Exception:
			server_prefs = []
	roblox_user_id = int(rv["roblox_user_id"]) if rv and rv["roblox_user_id"] else None
	avatar_url = get_avatar_url(roblox_user_id) if roblox_user_id else None
	is_verified = bool(rv["is_verified"]) if rv else False
	roblox_username = rv["roblox_username"] if rv else None
	return render_template(
		"profile_view.html",
		user=user,
		server_prefs=server_prefs,
		rv=rv,
		avatar_url=avatar_url,
		is_verified=is_verified,
		roblox_username=roblox_username,
	)


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
	if request.method == "POST":
		age = request.form.get("age")
		gender = request.form.get("gender")
		bio = request.form.get("bio")
		playstyle = request.form.get("playstyle")
		servers = request.form.get("servers", "")
		server_preferences = json.dumps([s.strip() for s in servers.split(',') if s.strip()])
		conn = connect()
		cur = conn.cursor()
		cur.execute(
			"""
			UPDATE users SET age = ?, gender = ?, bio = ?, playstyle = ?, server_preferences = ?, updated_at = CURRENT_TIMESTAMP
			WHERE id = ?
			""",
			(age, gender, bio, playstyle, server_preferences, current_user.id),
		)
		conn.commit()
		conn.close()
		flash("Profile updated", "success")
		return redirect(url_for("profile.view_profile"))
	# load current
	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE id = ?", (current_user.id,))
	user = cur.fetchone()
	conn.close()
	return render_template("profile_edit.html", user=user)


@profile_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_profile():
	if request.method == "POST":
		age = request.form.get("age")
		gender = request.form.get("gender")
		bio = request.form.get("bio")
		playstyle = request.form.get("playstyle")
		servers = request.form.get("servers", "")
		server_preferences = json.dumps([s.strip() for s in servers.split(',') if s.strip()])
		conn = connect()
		cur = conn.cursor()
		cur.execute(
			"""
			UPDATE users SET age = ?, gender = ?, bio = ?, playstyle = ?, server_preferences = ?, updated_at = CURRENT_TIMESTAMP
			WHERE id = ?
			""",
			(age, gender, bio, playstyle, server_preferences, current_user.id),
		)
		conn.commit()
		conn.close()
		flash("Profile created/updated", "success")
		return redirect(url_for("profile.view_profile"))
	return render_template("profile_create.html")


@profile_bp.route("/verify", methods=["GET", "POST"])
@login_required
def verify_roblox():
	if request.method == "POST":
		roblox_username = request.form.get("roblox_username", "").strip()
		resolved = resolve_roblox_username(roblox_username)
		if not resolved:
			flash("Roblox username not found", "error")
			return redirect(url_for("profile.verify_roblox"))
		roblox_user_id = int(resolved.get("id"))
		is_verified = check_roblox_verification(roblox_user_id)
		conn = connect()
		cur = conn.cursor()
		cur.execute(
			"""
			INSERT INTO roblox_verification (discord_id, roblox_username, roblox_user_id, is_verified, verified_at)
			VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
			ON CONFLICT(discord_id) DO UPDATE SET roblox_username=excluded.roblox_username, roblox_user_id=excluded.roblox_user_id, is_verified=excluded.is_verified, verified_at=CURRENT_TIMESTAMP
			""",
			(str(current_user.id), roblox_username, roblox_user_id, 1 if is_verified else 0),
		)
		conn.commit()
		conn.close()
		flash("Roblox verified" if is_verified else "Verification phrase not found in bio", "info")
		return redirect(url_for("profile.view_profile"))
	return render_template("profile_verify.html")
