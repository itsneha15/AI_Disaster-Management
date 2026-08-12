from cryptography.fernet import Fernet
from pathlib import Path

KEY_PATH = Path("config/master.key")

# Create config directory if it doesn't exist
KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

if not KEY_PATH.exists():
    key = Fernet.generate_key()

    with open(KEY_PATH, "wb") as key_file:
        key_file.write(key)

    print("✅ Master key generated successfully!")

else:
    print("ℹ️ Master key already exists.")