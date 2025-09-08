import os
import requests

ROBLOX_USERS_API = "https://users.roblox.com/v1/usernames/users"
ROBLOX_USER_API = "https://users.roblox.com/v1/users"
ROBLOX_THUMB_API = "https://thumbnails.roblox.com/v1/users/avatar-headshot"
VERIFICATION_PHRASE = os.getenv("VERIFICATION_PHRASE", "anomidate").lower()


def resolve_roblox_username(username: str):
	payload = {"usernames": [username], "excludeBannedUsers": True}
	r = requests.post(ROBLOX_USERS_API, json=payload, timeout=10)
	if r.status_code != 200:
		return None
	data = r.json().get("data", [])
	return data[0] if data else None


def get_roblox_user_info(user_id: int):
	r = requests.get(f"{ROBLOX_USER_API}/{user_id}", timeout=10)
	if r.status_code != 200:
		return None
	return r.json()


def check_roblox_verification(user_id: int) -> bool:
	info = get_roblox_user_info(user_id)
	if not info:
		return False
	desc = (info.get("description") or "").lower()
	return VERIFICATION_PHRASE in desc


def get_avatar_url(user_id: int, size: str = "150x150", circular: bool = False) -> str:
	params = {
		"userIds": str(user_id),
		"size": size,
		"format": "Png",
		"isCircular": "true" if circular else "false",
	}
	r = requests.get(ROBLOX_THUMB_API, params=params, timeout=10)
	if r.status_code == 200:
		data = r.json().get("data") or []
		if data:
			return data[0].get("imageUrl") or ""
	return ""
