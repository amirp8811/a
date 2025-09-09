import sqlite3
from pathlib import Path

DB_PATH = Path("anomic_dating.db")


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=5000;

CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	discord_id TEXT UNIQUE,
	username TEXT NOT NULL,
	password_hash TEXT,
	age INTEGER,
	gender TEXT,
	bio TEXT,
	playstyle TEXT,
	server_preferences TEXT,
	timezone TEXT,
	availability TEXT,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roblox_verification (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	discord_id TEXT UNIQUE NOT NULL,
	roblox_username TEXT NOT NULL,
	roblox_user_id INTEGER NOT NULL,
	verified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	is_verified BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS matches (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	swiper_id TEXT NOT NULL,
	swiped_id TEXT NOT NULL,
	action TEXT NOT NULL CHECK (action IN ('like','pass')),
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	UNIQUE(swiper_id, swiped_id)
);

CREATE TABLE IF NOT EXISTS mutual_matches (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user1_id TEXT NOT NULL,
	user2_id TEXT NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	UNIQUE(user1_id, user2_id)
);

CREATE TABLE IF NOT EXISTS daily_swipes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id TEXT NOT NULL,
	swipe_date DATE NOT NULL,
	swipe_count INTEGER DEFAULT 0,
	UNIQUE(user_id, swipe_date)
);

CREATE TABLE IF NOT EXISTS messages (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	sender_id TEXT NOT NULL,
	receiver_id TEXT NOT NULL,
	message_content TEXT NOT NULL,
	sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	is_read BOOLEAN DEFAULT FALSE
);
"""


def connect():
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	return conn


def _migrate(conn: sqlite3.Connection):
	cur = conn.cursor()
	# Add users.email if missing
	cur.execute("PRAGMA table_info(users)")
	cols = [r[1] for r in cur.fetchall()]
	if "email" not in cols:
		cur.execute("ALTER TABLE users ADD COLUMN email TEXT")
		conn.commit()
	# Add moderation columns if missing
	cur.execute("PRAGMA table_info(users)")
	cols = [r[1] for r in cur.fetchall()]
	if "banned" not in cols:
		cur.execute("ALTER TABLE users ADD COLUMN banned BOOLEAN DEFAULT FALSE")
		conn.commit()
	cur.execute("PRAGMA table_info(users)")
	cols = [r[1] for r in cur.fetchall()]
	if "suspended_until" not in cols:
		cur.execute("ALTER TABLE users ADD COLUMN suspended_until DATETIME")
		conn.commit()
	# Password reset table
	cur.execute(
		"""
		CREATE TABLE IF NOT EXISTS password_resets (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			email TEXT NOT NULL,
			code TEXT NOT NULL,
			expires_at DATETIME NOT NULL,
			used BOOLEAN DEFAULT FALSE,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)
	conn.commit()
	# Roblox verification: add numeric user_id and backfill from discord_id if numeric
	cur.execute("PRAGMA table_info(roblox_verification)")
	cols = [r[1] for r in cur.fetchall()]
	if "user_id" not in cols:
		cur.execute("ALTER TABLE roblox_verification ADD COLUMN user_id INTEGER")
		conn.commit()
		cur.execute("UPDATE roblox_verification SET user_id = CAST(discord_id AS INTEGER) WHERE user_id IS NULL AND discord_id GLOB '[0-9]*'")
		conn.commit()
	# Mutual matches: add numeric columns and backfill from existing text ids if numeric
	cur.execute("PRAGMA table_info(mutual_matches)")
	cols = [r[1] for r in cur.fetchall()]
	if "user1_user_id" not in cols:
		cur.execute("ALTER TABLE mutual_matches ADD COLUMN user1_user_id INTEGER")
		conn.commit()
	if "user2_user_id" not in cols:
		cur.execute("ALTER TABLE mutual_matches ADD COLUMN user2_user_id INTEGER")
		conn.commit()
	cur.execute("UPDATE mutual_matches SET user1_user_id = CAST(user1_id AS INTEGER) WHERE user1_user_id IS NULL AND user1_id GLOB '[0-9]*'")
	cur.execute("UPDATE mutual_matches SET user2_user_id = CAST(user2_id AS INTEGER) WHERE user2_user_id IS NULL AND user2_id GLOB '[0-9]*'")
	conn.commit()


def init_db():
	conn = connect()
	cur = conn.cursor()
	cur.executescript(SCHEMA_SQL)
	conn.commit()
	_migrate(conn)
	conn.close()


if __name__ == "__main__":
	init_db()
	print(f"Initialized DB at {DB_PATH}")
