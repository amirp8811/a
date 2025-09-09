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


@admin_bp.route("/users")
def users():
	if not _is_admin():
		return redirect(url_for("admin.login"))
	q = request.args.get("q", "").strip()
	page = max(int(request.args.get("page", 1) or 1), 1)
	page_size = 25
	offset = (page - 1) * page_size
	conn = connect()
	cur = conn.cursor()
	params = []
	where = ""
	if q:
		where = "WHERE username LIKE ? OR discord_id LIKE ?"
		like = f"%{q}%"
		params.extend([like, like])
	cur.execute(f"SELECT COUNT(*) AS c FROM users {where}", params)
	row = cur.fetchone()
	total = row["c"] if row else 0
	cur.execute(
		f"""
		SELECT id, discord_id, username, age, gender, banned, suspended_until, created_at
		FROM users
		{where}
		ORDER BY created_at DESC
		LIMIT ? OFFSET ?
		""",
		[*params, page_size, offset],
	)
	users = cur.fetchall()
	conn.close()
	pages = (total + page_size - 1) // page_size
	return render_template("admin_users.html", users=users, q=q, page=page, pages=pages, total=total)


@admin_bp.route("/users/<int:user_id>")
def user_detail(user_id: int):
	if not _is_admin():
		return redirect(url_for("admin.login"))
	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
	user = cur.fetchone()
	if not user:
		conn.close()
		flash("User not found", "error")
		return redirect(url_for("admin.users"))
	# Stats
	cur.execute("SELECT COUNT(*) AS c FROM messages WHERE sender_id = ? OR receiver_id = ?", (str(user["id"]), str(user["id"])) )
	msg_count = (cur.fetchone() or {"c": 0})["c"]
	cur.execute("SELECT COUNT(*) AS c FROM mutual_matches WHERE user1_id = ? OR user2_id = ?", (str(user["discord_id"]), str(user["discord_id"])) )
	match_count = (cur.fetchone() or {"c": 0})["c"]
	# recent matches by discord id linkage
	cur.execute(
		"""
		SELECT mm.id, mm.user1_id, mm.user2_id, mm.created_at
		FROM mutual_matches mm
		WHERE mm.user1_id = ? OR mm.user2_id = ?
		ORDER BY mm.created_at DESC
		LIMIT 20
		""",
		(str(user["discord_id"]), str(user["discord_id"]))
	)
	matches = cur.fetchall()
	conn.close()
	return render_template("admin_user_detail.html", user=user, msg_count=msg_count, match_count=match_count, matches=matches)


@admin_bp.route("/users/<int:user_id>/ban", methods=["POST"])
def ban_user(user_id: int):
	if not _is_admin():
		return redirect(url_for("admin.login"))
	conn = connect()
	cur = conn.cursor()
	cur.execute("UPDATE users SET banned = TRUE, suspended_until = NULL WHERE id = ?", (user_id,))
	conn.commit()
	conn.close()
	flash("User banned", "success")
	return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/unban", methods=["POST"])
def unban_user(user_id: int):
	if not _is_admin():
		return redirect(url_for("admin.login"))
	conn = connect()
	cur = conn.cursor()
	cur.execute("UPDATE users SET banned = FALSE WHERE id = ?", (user_id,))
	conn.commit()
	conn.close()
	flash("User unbanned", "success")
	return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/suspend", methods=["POST"])
def suspend_user(user_id: int):
	if not _is_admin():
		return redirect(url_for("admin.login"))
	days = int(request.form.get("days", 0) or 0)
	if days <= 0:
		flash("Provide a valid suspension duration (days)", "error")
		return redirect(url_for("admin.user_detail", user_id=user_id))
	conn = connect()
	cur = conn.cursor()
	cur.execute("UPDATE users SET suspended_until = datetime('now', ?), banned = FALSE WHERE id = ?", (f"+{days} days", user_id))
	conn.commit()
	conn.close()
	flash(f"User suspended for {days} days", "success")
	return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/unsuspend", methods=["POST"])
def unsuspend_user(user_id: int):
	if not _is_admin():
		return redirect(url_for("admin.login"))
	conn = connect()
	cur = conn.cursor()
	cur.execute("UPDATE users SET suspended_until = NULL WHERE id = ?", (user_id,))
	conn.commit()
	conn.close()
	flash("User suspension cleared", "success")
	return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id: int):
	if not _is_admin():
		return redirect(url_for("admin.login"))
	conn = connect()
	cur = conn.cursor()
	# Cascade delete related content
	cur.execute("DELETE FROM messages WHERE sender_id = ? OR receiver_id = ?", (str(user_id), str(user_id)))
	cur.execute("DELETE FROM matches WHERE swiper_id = ? OR swiped_id = ?", (str(user_id), str(user_id)))
	cur.execute("DELETE FROM mutual_matches WHERE user1_id = ? OR user2_id = ?", (str(user_id), str(user_id)))
	cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
	conn.commit()
	conn.close()
	flash("User deleted", "success")
	return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/messages/delete", methods=["POST"])
def delete_messages(user_id: int):
	if not _is_admin():
		return redirect(url_for("admin.login"))
	peer = request.form.get("peer_id", "").strip()
	if not peer:
		flash("Provide peer_id to delete conversation", "error")
		return redirect(url_for("admin.user_detail", user_id=user_id))
	conn = connect()
	cur = conn.cursor()
	cur.execute(
		"DELETE FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)",
		(str(user_id), peer, peer, str(user_id)),
	)
	conn.commit()
	conn.close()
	flash("Conversation deleted", "success")
	return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/unmatch", methods=["POST"])
def unmatch(user_id: int):
	if not _is_admin():
		return redirect(url_for("admin.login"))
	peer_discord = request.form.get("peer_discord_id", "").strip()
	if not peer_discord:
		flash("Provide peer_discord_id", "error")
		return redirect(url_for("admin.user_detail", user_id=user_id))
	conn = connect()
	cur = conn.cursor()
	# Remove mutual match rows where either side equals user discord id or peer discord id
	cur.execute(
		"DELETE FROM mutual_matches WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)",
		(str(peer_discord), str(peer_discord), str(peer_discord), str(peer_discord)),
	)
	# Also remove any like pairs between the two users if present (by numeric user ids in matches)
	cur.execute(
		"DELETE FROM matches WHERE (swiper_id = ? AND swiped_id = ?) OR (swiper_id = ? AND swiped_id = ?)",
		(str(user_id), peer_discord, peer_discord, str(user_id)),
	)
	conn.commit()
	conn.close()
	flash("Unmatched users", "success")
	return redirect(url_for("admin.user_detail", user_id=user_id))
