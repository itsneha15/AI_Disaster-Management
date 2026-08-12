from cryptography.fernet import Fernet
from pathlib import Path

KEY_FILE = Path("config/master.key")


def load_key():
    """Load the encryption key."""
    with open(KEY_FILE, "rb") as file:
        return file.read()


cipher = Fernet(load_key())


def encrypt_file(input_path, output_path):
    """
    Encrypt a file and save it to the output path.
    """
    with open(input_path, "rb") as file:
        file_data = file.read()

    encrypted_data = cipher.encrypt(file_data)

    with open(output_path, "wb") as file:
        file.write(encrypted_data)

    print(f"✅ File encrypted: {output_path}")


def decrypt_file(input_path, output_path):
    """
    Decrypt a file and restore it.
    """
    with open(input_path, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    with open(output_path, "wb") as file:
        file.write(decrypted_data)

    print(f"✅ File restored: {output_path}")