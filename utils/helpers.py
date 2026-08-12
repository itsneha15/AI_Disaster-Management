import hashlib


def calculate_sha256(file_path):

    sha256 = hashlib.sha256()

    try:

        with open(file_path, "rb") as file:

            while True:

                data = file.read(4096)

                if not data:
                    break

                sha256.update(data)

        return sha256.hexdigest()

    except Exception:

        return None