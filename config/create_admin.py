import bcrypt
import json
from pathlib import Path

ADMIN_FILE = Path("config/admin.json")

admin = {
    "username": "admin",
    "name": "System Administrator",
    "role": "Administrator",
    "password": bcrypt.hashpw(
        "admin123".encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")
}

with open(ADMIN_FILE, "w") as f:
    json.dump(admin, f, indent=4)

print("✅ Admin created successfully!")