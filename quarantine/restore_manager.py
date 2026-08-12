from pathlib import Path
import os

from quarantine.encryption import decrypt_file
from quarantine.hashing import calculate_sha256
from quarantine.metadata_manager import MetadataManager
from quarantine.logger import log_event


# =========================================================
# QUARANTINE STORAGE
# =========================================================

if os.getenv("VERCEL"):
    ENCRYPTED_FOLDER = Path(
        "/tmp/secure_repository/encrypted"
    )
else:
    ENCRYPTED_FOLDER = Path(
        "secure_repository/encrypted"
    )


# =========================================================
# RESTORE FILE
# =========================================================

def restore_file(file_id):

    file = MetadataManager.find(
        file_id
    )

    if not file:

        return False, "File not found."


    # -----------------------------------------------------
    # Encrypted quarantine file
    # -----------------------------------------------------

    encrypted_path = (
        ENCRYPTED_FOLDER /
        file["stored_name"]
    )


    if not encrypted_path.exists():

        return (
            False,
            "Encrypted quarantine file not found."
        )


    # -----------------------------------------------------
    # Original restore location
    # -----------------------------------------------------

    restore_path = Path(
        file["original_path"]
    )


    # -----------------------------------------------------
    # Vercel
    # -----------------------------------------------------
    #
    # The original path belongs to the user's local
    # computer and does not exist inside Vercel.
    #
    # Therefore restore to /tmp while running on Vercel.
    #

    if os.getenv("VERCEL"):

        restore_path = (
            Path("/tmp/ai_disaster_restored")
            / file["original_name"]
        )


    # -----------------------------------------------------
    # Create writable restore directory
    # -----------------------------------------------------

    try:

        restore_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    except OSError as error:

        return (
            False,
            f"Could not create restore directory: {error}"
        )


    # -----------------------------------------------------
    # Decrypt
    # -----------------------------------------------------

    try:

        decrypt_file(
            encrypted_path,
            restore_path
        )

    except Exception as error:

        return (
            False,
            f"Decryption failed: {error}"
        )


    # -----------------------------------------------------
    # Verify integrity
    # -----------------------------------------------------

    try:

        restored_hash = (
            calculate_sha256(
                restore_path
            )
        )

    except Exception as error:

        restore_path.unlink(
            missing_ok=True
        )

        return (
            False,
            f"Could not calculate restored hash: {error}"
        )


    if restored_hash != file["sha256"]:

        restore_path.unlink(
            missing_ok=True
        )

        return (
            False,
            "Integrity verification failed."
        )


    # -----------------------------------------------------
    # Mark restored
    # -----------------------------------------------------

    MetadataManager.mark_restored(
        file_id
    )


    # -----------------------------------------------------
    # Log
    # -----------------------------------------------------

    log_event(
        f'{file["original_name"]} restored'
    )


    return (
        True,
        "File restored successfully."
    )