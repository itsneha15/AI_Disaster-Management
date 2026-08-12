from pathlib import Path
from quarantine.encryption import encrypt_file, decrypt_file

encrypted_dir = Path("secure_repository/encrypted")
encrypted_dir.mkdir(parents=True, exist_ok=True)

encrypt_file(
    "monitored_folder/sample.txt",
    "secure_repository/encrypted/sample.enc"
)

decrypt_file(
    "secure_repository/encrypted/sample.enc",
    "secure_repository/restored/sample.txt"
)