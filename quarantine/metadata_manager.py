import json
import os
from os import path
from pathlib import Path
from datetime import datetime

METADATA_FILE = Path("secure_repository/metadata/metadata.json")


class MetadataManager:

    @staticmethod
    def load():

        if not METADATA_FILE.exists():
            return []

        with open(METADATA_FILE, "r") as f:
            return json.load(f)

    @staticmethod
    def save(data):

        with open(METADATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def next_id():

        data = MetadataManager.load()

        if len(data) == 0:
            return 1

        return max(item["id"] for item in data) + 1



    @staticmethod
    def add(
        original_path,
        stored_name,
        sha256,
        risk,
        risk_score,
    ):

        data = MetadataManager.load()

        path = Path(original_path)

        # Decide the status based on the detected risk
        if risk == "Safe":
            status = "Safe"
        else:
            status = "Quarantined"

        entry = {
            "id": MetadataManager.next_id(),
            "original_name": path.name,
            "original_path": str(path),
            "stored_name": stored_name,
            "sha256": sha256,
            "risk": risk,
            "risk_score": risk_score,
            "size": os.path.getsize(path),
            "status": status,
            "restored": False,
            "timestamp": datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
        }

        data.append(entry)

        MetadataManager.save(data)

        return entry

    @staticmethod
    def all():

        return MetadataManager.load()

    @staticmethod
    def find(file_id):

        for item in MetadataManager.load():

            if item["id"] == file_id:

                return item

    @staticmethod
    def mark_restored(file_id):

        data = MetadataManager.load()

        for item in data:

            if item["id"] == file_id:

                item["status"] = "Restored"
                item["restored"] = True
                break

        MetadataManager.save(data)