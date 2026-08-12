from pathlib import Path

from quarantine.encryption import decrypt_file
from quarantine.hashing import calculate_sha256
from quarantine.metadata_manager import MetadataManager
from quarantine.logger import log_event


ENCRYPTED_FOLDER = Path("secure_repository/encrypted")


def restore_file(file_id):

    file = MetadataManager.find(file_id)

    if not file:

        return False, "File not found."

    encrypted_path = ENCRYPTED_FOLDER / file["stored_name"]

    restore_path = Path(file["original_path"])

    restore_path.parent.mkdir(parents=True, exist_ok=True)

    decrypt_file(
        encrypted_path,
        restore_path
    )

    restored_hash = calculate_sha256(restore_path)

    if restored_hash != file["sha256"]:

        restore_path.unlink(missing_ok=True)

        return False, "Integrity verification failed."

    MetadataManager.mark_restored(file_id)

    log_event(f"{file['original_name']} restored")

    return True, "File restored successfully."