from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from .db import connect
from .roblox import get_avatar_url

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/me")
@login_required
def me():
	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT id, username FROM users WHERE id = ?", (current_user.id,))
	user = cur.fetchone()
	cur.execute("SELECT roblox_user_id, roblox_username, is_verified FROM roblox_verification WHERE discord_id = ?", (str(current_user.id),))
	rv = cur.fetchone()
	conn.close()
	roblox = None
	if rv:
		avatar = get_avatar_url(int(rv["roblox_user_id"])) if rv["roblox_user_id"] else ""
		roblox = {"user_id": rv["roblox_user_id"], "username": rv["roblox_username"], "verified": bool(rv["is_verified"]), "avatarUrl": avatar}
	return jsonify({
		"id": user["id"],
		"username": user["username"],
		"roblox": roblox,
	})


@api_bp.get("/swipe/next")
@login_required
def swipe_next():
	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT id, username, age, gender, playstyle, server_preferences, bio FROM users WHERE id != ? ORDER BY RANDOM() LIMIT 1", (current_user.id,))
	row = cur.fetchone()
	if not row:
		conn.close()
		return jsonify({"profile": None})
	# get roblox for that user
	cur.execute("SELECT roblox_user_id FROM roblox_verification WHERE discord_id = ?", (str(row["id"]),))
	rv = cur.fetchone()
	conn.close()
	avatar = None
	roblox_user_id = None
	if rv and rv["roblox_user_id"]:
		roblox_user_id = int(rv["roblox_user_id"])
		avatar = get_avatar_url(roblox_user_id)
	return jsonify({
		"profile": {
			"id": row["id"],
			"username": row["username"],
			"age": row["age"],
			"gender": row["gender"],
			"playstyle": row["playstyle"],
			"servers": row["server_preferences"],
			"bio": row["bio"],
			"robloxUserId": roblox_user_id,
			"avatarUrl": avatar,
		}
	})
