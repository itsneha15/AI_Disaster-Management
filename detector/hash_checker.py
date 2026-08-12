import hashlib
from pathlib import Path

HASH_FILE = Path("detector/known_hashes.txt")


def calculate(file_path):

    sha = hashlib.sha256()

    with open(file_path, "rb") as f:

        while chunk := f.read(4096):
            sha.update(chunk)

    return sha.hexdigest()


def check_hash(file_path):

    if not HASH_FILE.exists():
        return 0

    file_hash = calculate(file_path)

    with open(HASH_FILE) as f:

        hashes = [x.strip() for x in f.readlines()]

    if file_hash in hashes:
        return 50

    return 0