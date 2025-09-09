from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import json
from .db import connect
from .roblox import resolve_roblox_username, check_roblox_verification, get_avatar_url
import os
import requests
from urllib.parse import urlencode

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
		flash("Resolving Roblox username...", "success")
		resolved = resolve_roblox_username(roblox_username)
		if not resolved:
			flash("Roblox username not found", "error")
			return redirect(url_for("profile.verify_roblox"))
		flash("Found user. Checking bio for verification phrase...", "success")
		roblox_user_id = int(resolved.get("id"))
		is_verified = check_roblox_verification(roblox_user_id)
		flash("Updating your verification status...", "success")
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


# Roblox OAuth2 (Sign in with Roblox) for verification
ROBLOX_CLIENT_ID = os.getenv("ROBLOX_CLIENT_ID")
ROBLOX_CLIENT_SECRET = os.getenv("ROBLOX_CLIENT_SECRET", "__SET_ME__")
ROBLOX_REDIRECT_URI = os.getenv("ROBLOX_REDIRECT_URI", "http://localhost:5000/profile/roblox/callback")
ROBLOX_AUTH_URL = "https://apis.roblox.com/oauth/v1/authorize"
ROBLOX_TOKEN_URL = "https://apis.roblox.com/oauth/v1/token"
ROBLOX_USERINFO_URL = "https://apis.roblox.com/oauth/v1/userinfo"


@profile_bp.route("/roblox/login")
@login_required
def roblox_oauth_login():
	if not ROBLOX_CLIENT_ID or not ROBLOX_REDIRECT_URI:
		flash("Roblox OAuth is not configured", "error")
		return redirect(url_for("profile.verify_roblox"))
	params = {
		"client_id": ROBLOX_CLIENT_ID,
		"redirect_uri": ROBLOX_REDIRECT_URI,
		"response_type": "code",
		"scope": "openid profile",
	}
	return redirect(f"{ROBLOX_AUTH_URL}?{urlencode(params)}")


@profile_bp.route("/roblox/callback")
@login_required
def roblox_oauth_callback():
	code = request.args.get("code")
	if not code:
		flash("Roblox sign-in failed: missing code", "error")
		return redirect(url_for("profile.verify_roblox"))
	data = {
		"client_id": ROBLOX_CLIENT_ID,
		"client_secret": ROBLOX_CLIENT_SECRET,
		"grant_type": "authorization_code",
		"code": code,
		"redirect_uri": ROBLOX_REDIRECT_URI,
	}
	headers = {"Content-Type": "application/x-www-form-urlencoded"}
	tr = requests.post(ROBLOX_TOKEN_URL, data=data, headers=headers, timeout=15)
	if tr.status_code != 200:
		flash("Roblox token exchange failed", "error")
		return redirect(url_for("profile.verify_roblox"))
	tok = tr.json()
	access_token = tok.get("access_token")
	if not access_token:
		flash("Roblox token missing", "error")
		return redirect(url_for("profile.verify_roblox"))
	ur = requests.get(ROBLOX_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}, timeout=15)
	if ur.status_code != 200:
		flash("Failed to fetch Roblox user", "error")
		return redirect(url_for("profile.verify_roblox"))
	ud = ur.json() or {}
	roblox_user_id = ud.get("sub") or ud.get("id")
	roblox_username = ud.get("name") or ud.get("preferred_username") or "roblox_user"
	try:
		roblox_user_id = int(str(roblox_user_id)) if roblox_user_id is not None else None
	except Exception:
		roblox_user_id = None
	if not roblox_user_id:
		flash("Roblox user information incomplete", "error")
		return redirect(url_for("profile.verify_roblox"))
	# Mark verified
	conn = connect()
	cur = conn.cursor()
	cur.execute(
		"""
		INSERT INTO roblox_verification (discord_id, roblox_username, roblox_user_id, is_verified, verified_at)
		VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
		ON CONFLICT(discord_id) DO UPDATE SET roblox_username=excluded.roblox_username, roblox_user_id=excluded.roblox_user_id, is_verified=1, verified_at=CURRENT_TIMESTAMP
		""",
		(str(current_user.id), roblox_username, roblox_user_id),
	)
	conn.commit()
	conn.close()
	flash("Roblox account verified via OAuth", "success")
	return redirect(url_for("profile.view_profile"))
