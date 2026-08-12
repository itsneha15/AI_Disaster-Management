from quarantine.metadata_manager import MetadataManager
from monitor.file_monitor import WATCH_FOLDERS


def get_dashboard_data():

    files = MetadataManager.all()

    total = len(files)

    critical = len([
        f for f in files
        if f["risk"] == "Critical"
    ])

    high = len([
        f for f in files
        if f["risk"] == "High"
    ])

    medium = len([
        f for f in files
        if f["risk"] == "Medium"
    ])

    safe = len([
        f for f in files
        if f["risk"] == "Safe"
    ])

    quarantined = len([
        f for f in files
        if f["status"] == "Quarantined"
    ])

    restored = len([
        f for f in files
        if f["status"] == "Restored"
    ])

    return {

        "scanned": total,

        "safe": safe,

        "quarantined": quarantined,

        "critical": critical,

        "high": high,

        "medium": medium,

        "restored": restored,

        "files": files[::-1],

        "watch_folders": [
            str(folder)
            for folder in WATCH_FOLDERS
        ]

    }