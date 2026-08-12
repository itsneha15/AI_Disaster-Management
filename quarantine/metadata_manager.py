import json
import os
from pathlib import Path
from datetime import datetime


# =========================================================
# METADATA STORAGE
# =========================================================

# Original project metadata location.
# This file can be READ on Vercel because it is part of the
# deployed project.
SOURCE_METADATA_FILE = Path(
    "secure_repository/metadata/metadata.json"
)


# Vercel's filesystem is read-only except for /tmp.
#
# Local:
#     secure_repository/metadata/metadata.json
#
# Vercel:
#     /tmp/secure_repository/metadata/metadata.json
if os.getenv("VERCEL"):
    METADATA_FILE = Path(
        "/tmp/secure_repository/metadata/metadata.json"
    )
else:
    METADATA_FILE = SOURCE_METADATA_FILE


class MetadataManager:

    # =====================================================
    # LOAD
    # =====================================================

    @staticmethod
    def load():

        # First try the runtime file.
        # On Vercel this is /tmp/...
        if METADATA_FILE.exists():

            try:

                with open(
                    METADATA_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:

                    return json.load(f)

            except (json.JSONDecodeError, OSError):

                return []


        # On Vercel, if /tmp doesn't contain metadata yet,
        # read the original bundled metadata file.
        if (
            os.getenv("VERCEL")
            and SOURCE_METADATA_FILE.exists()
        ):

            try:

                with open(
                    SOURCE_METADATA_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:

                    return json.load(f)

            except (json.JSONDecodeError, OSError):

                return []


        return []


    # =====================================================
    # SAVE
    # =====================================================

    @staticmethod
    def save(data):

        # Create the writable runtime directory.
        METADATA_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            METADATA_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )


    # =====================================================
    # NEXT ID
    # =====================================================

    @staticmethod
    def next_id():

        data = MetadataManager.load()

        if len(data) == 0:
            return 1

        return max(
            item["id"]
            for item in data
        ) + 1


    # =====================================================
    # ADD
    # =====================================================

    @staticmethod
    def add(
        original_path,
        stored_name,
        sha256,
        risk,
        risk_score,
    ):

        data = MetadataManager.load()

        file_path = Path(original_path)

        # Decide status based on detected risk.
        if risk == "Safe":
            status = "Safe"
        else:
            status = "Quarantined"

        # Safely determine file size.
        try:
            file_size = os.path.getsize(file_path)
        except OSError:
            file_size = 0

        entry = {

            "id": MetadataManager.next_id(),

            "original_name":
                file_path.name,

            "original_path":
                str(file_path),

            "stored_name":
                stored_name,

            "sha256":
                sha256,

            "risk":
                risk,

            "risk_score":
                risk_score,

            "size":
                file_size,

            "status":
                status,

            "restored":
                False,

            "timestamp":
                datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S"
                ),
        }

        data.append(entry)

        MetadataManager.save(data)

        return entry


    # =====================================================
    # ALL
    # =====================================================

    @staticmethod
    def all():

        return MetadataManager.load()


    # =====================================================
    # FIND
    # =====================================================

    @staticmethod
    def find(file_id):

        for item in MetadataManager.load():

            if item["id"] == file_id:

                return item

        return None


    # =====================================================
    # MARK RESTORED
    # =====================================================

    @staticmethod
    def mark_restored(file_id):

        data = MetadataManager.load()

        for item in data:

            if item["id"] == file_id:

                item["status"] = "Restored"

                item["restored"] = True

                break

        MetadataManager.save(data)