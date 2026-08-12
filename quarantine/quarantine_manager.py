from pathlib import Path
import os

from quarantine.hashing import calculate_sha256
from quarantine.encryption import encrypt_file
from quarantine.metadata_manager import MetadataManager
from quarantine.logger import log_event


# =========================================================
# QUARANTINE STORAGE
# =========================================================

# Local system:
#     secure_repository/encrypted
#
# Vercel:
#     /tmp/secure_repository/encrypted
#
# Vercel's deployed filesystem is read-only, so runtime
# quarantine files must be written to /tmp.

if os.getenv("VERCEL"):
    ENCRYPTED = Path(
        "/tmp/secure_repository/encrypted"
    )
else:
    ENCRYPTED = Path(
        "secure_repository/encrypted"
    )


# =========================================================
# QUARANTINE FILE
# =========================================================

def quarantine_file(file_path, risk, score):

    file_path = Path(file_path)

    # Make sure the writable quarantine directory exists.
    ENCRYPTED.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Calculate SHA256
    # -----------------------------------------------------

    sha256 = calculate_sha256(
        file_path
    )

    # -----------------------------------------------------
    # Generate quarantine ID
    # -----------------------------------------------------

    quarantine_id = MetadataManager.next_id()

    stored_name = (
        f"QF_{quarantine_id:06}.enc"
    )

    encrypted_file = (
        ENCRYPTED / stored_name
    )

    # -----------------------------------------------------
    # Encrypt
    # -----------------------------------------------------

    encrypt_file(
        file_path,
        encrypted_file
    )

    # -----------------------------------------------------
    # Save metadata
    # -----------------------------------------------------

    MetadataManager.add(
        original_path=file_path,
        stored_name=stored_name,
        sha256=sha256,
        risk=risk,
        risk_score=score
    )

    # -----------------------------------------------------
    # Remove original file
    # -----------------------------------------------------

    try:

        os.remove(file_path)

    except OSError as error:

        print(
            f"Warning: Could not remove "
            f"original file: {error}"
        )

    # -----------------------------------------------------
    # Log event
    # -----------------------------------------------------

    log_event(
        f"{file_path.name} quarantined"
    )

    print(
        f"Quarantine Successful: {stored_name}"
    )

    return stored_name