from datetime import date
import json
import random
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .db import connect
from .roblox import get_avatar_url

MAX_DAILY_SWIPES = 50

swipe_bp = Blueprint("swipe", __name__, url_prefix="/swipe")


def get_daily_swipe_count(user_id: int) -> int:
	conn = connect()
	cur = conn.cursor()
	today = date.today().isoformat()
	cur.execute("SELECT swipe_count FROM daily_swipes WHERE user_id = ? AND swipe_date = ?", (str(user_id), today))
	row = cur.fetchone()
	conn.close()
	return row[0] if row else 0


def increment_daily_swipes(user_id: int):
	conn = connect()
	cur = conn.cursor()
	today = date.today().isoformat()
	cur.execute(
		"""
		INSERT INTO daily_swipes (user_id, swipe_date, swipe_count) VALUES (?, ?, 1)
		ON CONFLICT(user_id, swipe_date) DO UPDATE SET swipe_count = swipe_count + 1
		""",
		(str(user_id), today),
	)
	conn.commit()
	conn.close()


@swipe_bp.route("/", methods=["GET"]) 
@login_required
def swipe_home():
	# filters
	age_min = request.args.get("age_min", type=int)
	age_max = request.args.get("age_max", type=int)
	gender = request.args.get("gender")
	playstyle = request.args.get("playstyle")

	# enforce limit
	if get_daily_swipe_count(current_user.id) >= MAX_DAILY_SWIPES:
		flash("Daily swipe limit reached", "error")
		return render_template("swipe_empty.html")

	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE id != ?", (current_user.id,))
	rows = cur.fetchall()
	# build map of roblox ids
	ids = [str(r["id"]) for r in rows]
	rmap = {}
	if ids:
		cur.execute("SELECT discord_id, roblox_user_id FROM roblox_verification WHERE discord_id IN (%s)" % ",".join(["?"]*len(ids)), ids)
		for rid, ruid in cur.fetchall():
			rmap[rid] = ruid
	conn.close()

	candidates = []
	for r in rows:
		if age_min is not None and (r["age"] or 0) < age_min:
			continue
		if age_max is not None and (r["age"] or 0) > age_max:
			continue
		if gender and (r["gender"] or '').lower() != gender.lower():
			continue
		if playstyle and (r["playstyle"] or '').lower() != playstyle.lower():
			continue
		candidates.append(r)

	if not candidates:
		return render_template("swipe_empty.html")

	profile = random.choice(candidates)
	server_prefs = []
	if profile["server_preferences"]:
		try:
			server_prefs = json.loads(profile["server_preferences"]) or []
		except Exception:
			server_prefs = []
	avatar_url = None
	roblox_id = rmap.get(str(profile["id"]))
	if roblox_id:
		avatar_url = get_avatar_url(int(roblox_id)) or None
	return render_template("swipe_card.html", profile=profile, server_prefs=server_prefs, avatar_url=avatar_url)


@swipe_bp.route("/like/<int:target_id>")
@login_required
def like_user(target_id: int):
	if get_daily_swipe_count(current_user.id) >= MAX_DAILY_SWIPES:
		flash("Daily swipe limit reached", "error")
		return redirect(url_for("swipe.swipe_home"))
	conn = connect()
	cur = conn.cursor()
	cur.execute(
		"INSERT OR REPLACE INTO matches (swiper_id, swiped_id, action) VALUES (?, ?, 'like')",
		(str(current_user.id), str(target_id)),
	)
	conn.commit()
	conn.close()
	increment_daily_swipes(current_user.id)
	flash("You liked this profile", "success")
	return redirect(url_for("swipe.swipe_home"))


@swipe_bp.route("/pass/<int:target_id>")
@login_required
def pass_user(target_id: int):
	if get_daily_swipe_count(current_user.id) >= MAX_DAILY_SWIPES:
		flash("Daily swipe limit reached", "error")
		return redirect(url_for("swipe.swipe_home"))
	conn = connect()
	cur = conn.cursor()
	cur.execute(
		"INSERT OR REPLACE INTO matches (swiper_id, swiped_id, action) VALUES (?, ?, 'pass')",
		(str(current_user.id), str(target_id)),
	)
	conn.commit()
	conn.close()
	increment_daily_swipes(current_user.id)
	flash("You passed this profile", "info")
	return redirect(url_for("swipe.swipe_home"))
