from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .db import connect

matches_bp = Blueprint("matches", __name__, url_prefix="/")


def _get_mutual_matches(user_id: int):
	conn = connect()
	cur = conn.cursor()
	cur.execute(
		"""
		SELECT u.* FROM users u
		WHERE u.id != ?
		AND EXISTS (
			SELECT 1 FROM matches m1 WHERE m1.swiper_id = ? AND m1.swiped_id = u.id AND m1.action = 'like'
		)
		AND EXISTS (
			SELECT 1 FROM matches m2 WHERE m2.swiper_id = u.id AND m2.swiped_id = ? AND m2.action = 'like'
		)
		ORDER BY u.username COLLATE NOCASE
		""",
		(user_id, str(user_id), str(user_id)),
	)
	rows = cur.fetchall()
	conn.close()
	return rows


@matches_bp.route("matches")
@login_required
def matches_list():
	rows = _get_mutual_matches(current_user.id)
	return render_template("matches.html", matches=rows)


@matches_bp.route("messages/<int:other_id>", methods=["GET", "POST"])
@login_required
def conversation(other_id: int):
	# Allow chatting only if mutual like
	rows = _get_mutual_matches(current_user.id)
	if not any(r["id"] == other_id for r in rows):
		flash("You can only message your matches", "error")
		return redirect(url_for("matches.matches_list"))
	conn = connect()
	cur = conn.cursor()
	if request.method == "POST":
		content = request.form.get("content", "").strip()
		if content:
			cur.execute(
				"INSERT INTO messages (sender_id, receiver_id, message_content) VALUES (?, ?, ?)",
				(str(current_user.id), str(other_id), content),
			)
			conn.commit()
			flash("Message sent", "success")
		return redirect(url_for("matches.conversation", other_id=other_id))
	# fetch conversation
	cur.execute(
		"""
		SELECT m.*, u1.username AS sender_username, u2.username AS receiver_username
		FROM messages m
		JOIN users u1 ON u1.discord_id = m.sender_id
		JOIN users u2 ON u2.discord_id = m.receiver_id
		WHERE (m.sender_id = ? AND m.receiver_id = ?) OR (m.sender_id = ? AND m.receiver_id = ?)
		ORDER BY m.sent_at ASC
		""",
		(str(current_user.id), str(other_id), str(other_id), str(current_user.id)),
	)
	msgs = cur.fetchall()
	# get other user
	cur.execute("SELECT * FROM users WHERE id = ?", (other_id,))
	other = cur.fetchone()
	conn.close()
	return render_template("conversation.html", other=other, messages=msgs)
