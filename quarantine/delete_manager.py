from pathlib import Path
import os

from quarantine.metadata_manager import MetadataManager
from quarantine.logger import log_event

ENCRYPTED = Path("secure_repository/encrypted")


def delete_file(file_id):

    data = MetadataManager.load()

    new_data = []

    for item in data:

        if item["id"] == file_id:

            encrypted_file = ENCRYPTED / item["stored_name"]

            if encrypted_file.exists():

                os.remove(encrypted_file)

            log_event(
                f'{item["original_name"]} permanently deleted'
            )

            continue

        new_data.append(item)

    MetadataManager.save(new_data)

    print("File Deleted Successfully")