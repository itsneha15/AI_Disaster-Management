import json
import bcrypt
from pathlib import Path

ADMIN_FILE = Path("config/admin.json")


def authenticate(username, password):

    if not ADMIN_FILE.exists():
        return False

    with open(ADMIN_FILE, "r") as f:
        admin = json.load(f)

    if username != admin.get("username"):
        return False

    stored_hash = admin.get("password", "")

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )
    except ValueError:
        print("❌ Invalid bcrypt hash found in admin.json")
        return False
