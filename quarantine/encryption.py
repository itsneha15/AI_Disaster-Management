from cryptography.fernet import Fernet
from pathlib import Path
import os


# ---------------------------------------------------------
# Encryption key
# ---------------------------------------------------------

KEY_FILE = Path("config/master.key")


def load_key():
    """
    Load the encryption key.

    Priority:
    1. ENCRYPTION_KEY environment variable
    2. Local config/master.key file

    Vercel/serverless deployments should use
    ENCRYPTION_KEY instead of a local key file.
    """

    env_key = os.getenv("ENCRYPTION_KEY")

    if env_key:
        return env_key.encode()

    if KEY_FILE.exists():
        with open(KEY_FILE, "rb") as file:
            return file.read().strip()

    raise RuntimeError(
        "Encryption key is not configured. "
        "Set ENCRYPTION_KEY environment variable "
        "or create config/master.key."
    )


def get_cipher():
    """
    Create the Fernet cipher only when encryption
    or decryption is actually required.
    """

    return Fernet(load_key())


# ---------------------------------------------------------
# Encrypt
# ---------------------------------------------------------

def encrypt_file(input_path, output_path):
    """
    Encrypt a file and save it to output_path.
    """

    cipher = get_cipher()

    with open(input_path, "rb") as file:
        file_data = file.read()

    encrypted_data = cipher.encrypt(file_data)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as file:
        file.write(encrypted_data)

    print(f"File encrypted: {output_path}")


# ---------------------------------------------------------
# Decrypt
# ---------------------------------------------------------

def decrypt_file(input_path, output_path):
    """
    Decrypt a file and restore it to output_path.
    """

    cipher = get_cipher()

    with open(input_path, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as file:
        file.write(decrypted_data)

    print(f"File restored: {output_path}")