import os
from flask import Flask, render_template, redirect, url_for, request, make_response
from flask_login import LoginManager, current_user
from flask_cors import CORS

from .auth import auth_bp, login_manager
from .routes_profile import profile_bp
from .routes_swipe import swipe_bp
from .routes_matches import matches_bp
from .api import api_bp
from .admin import admin_bp
from .db import init_db, connect


def create_app():
	app = Flask(__name__, template_folder="templates", static_folder="static")
	app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET", "dev-secret-change-me")
	app.config.update(
		SESSION_COOKIE_HTTPONLY=True,
		SESSION_COOKIE_SAMESITE="Lax",
	)

	# CORS for API (dev)
	CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]}}, supports_credentials=True)

	# DB
	init_db()

	# Auth
	app.register_blueprint(auth_bp)
	login_manager.init_app(app)

	# Blueprints
	app.register_blueprint(profile_bp)
	app.register_blueprint(swipe_bp)
	app.register_blueprint(matches_bp)
	app.register_blueprint(api_bp)
	app.register_blueprint(admin_bp)

	@app.after_request
	def set_security_headers(resp):
		resp.headers.setdefault("X-Content-Type-Options", "nosniff")
		resp.headers.setdefault("X-Frame-Options", "DENY")
		resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
		resp.headers.setdefault("Permissions-Policy", "geolocation=(), camera=(), microphone=()")
		return resp

	@app.before_request
	def guard_flow():
		path = request.path
		public = {"/welcome", "/health", "/auth/login", "/auth/register", "/auth/forgot", "/auth/reset", "/admin/login"}
		if any(path == p or path.startswith("/static/") or path.startswith("/api/") for p in public):
			return None
		if path.startswith("/admin"):
			return None
		if not current_user.is_authenticated:
			return redirect(url_for("welcome"))
		conn = connect()
		cur = conn.cursor()
		cur.execute("SELECT roblox_user_id, is_verified FROM roblox_verification WHERE discord_id = ?", (str(current_user.id),))
		row = cur.fetchone()
		conn.close()
		if not row or not row["is_verified"]:
			if path not in ("/profile/verify",):
				return redirect(url_for("profile.verify_roblox"))
		return None

	@app.route("/")
	def index():
		if not current_user.is_authenticated:
			return redirect(url_for("welcome"))
		return render_template("index.html")

	@app.route("/welcome")
	def welcome():
		resp = make_response(render_template("welcome.html"))
		if not request.cookies.get("anomidate_visited"):
			resp.set_cookie("anomidate_visited", "1", max_age=60*60*24*365, httponly=True, samesite="Lax")
		return resp

	@app.route("/health")
	def health():
		return {"ok": True}

	return app


if __name__ == "__main__":
	app = create_app()
	app.run(debug=True)
