from pathlib import Path
import os

from quarantine.hashing import calculate_sha256
from quarantine.encryption import encrypt_file
from quarantine.metadata_manager import MetadataManager
from quarantine.logger import log_event

ENCRYPTED = Path("secure_repository/encrypted")


def quarantine_file(file_path, risk, score):

    file_path = Path(file_path)

    ENCRYPTED.mkdir(exist_ok=True)

    sha256 = calculate_sha256(file_path)

    quarantine_id = MetadataManager.next_id()

    stored_name = f"QF_{quarantine_id:06}.enc"

    encrypted_file = ENCRYPTED / stored_name

    encrypt_file(
        file_path,
        encrypted_file
    )

    MetadataManager.add(

        original_path=file_path,

        stored_name=stored_name,

        sha256=sha256,

        risk=risk,
        risk_score=score

    )

    os.remove(file_path)

    log_event(

        f"{file_path.name} quarantined"

    )

    print("Quarantine Successful")