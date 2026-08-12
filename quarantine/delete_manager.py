from pathlib import Path
import os

from quarantine.metadata_manager import MetadataManager
from quarantine.logger import log_event


# =========================================================
# QUARANTINE STORAGE
# =========================================================

if os.getenv("VERCEL"):
    ENCRYPTED = Path(
        "/tmp/secure_repository/encrypted"
    )
else:
    ENCRYPTED = Path(
        "secure_repository/encrypted"
    )


# =========================================================
# DELETE QUARANTINED FILE
# =========================================================

def delete_file(file_id):

    data = MetadataManager.load()

    new_data = []

    for item in data:

        if item["id"] == file_id:

            encrypted_file = (
                ENCRYPTED /
                item["stored_name"]
            )

            if encrypted_file.exists():

                try:

                    os.remove(
                        encrypted_file
                    )

                except OSError as error:

                    print(
                        f"Warning: Could not delete "
                        f"encrypted file: {error}"
                    )

            log_event(
                f'{item["original_name"]} '
                f'permanently deleted'
            )

            continue

        new_data.append(item)

    MetadataManager.save(
        new_data
    )

    return True