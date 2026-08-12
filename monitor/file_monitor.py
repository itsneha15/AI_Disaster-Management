try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:  # pragma: no cover
    Observer = None

    class FileSystemEventHandler:
        pass

    WATCHDOG_AVAILABLE = False

from pathlib import Path
import time

from detector.classifier import classify_file
from quarantine.quarantine_manager import quarantine_file
from quarantine.metadata_manager import MetadataManager
from quarantine.hashing import calculate_sha256


# ==========================================================
# Automatically Detect User Folders
# ==========================================================

HOME = Path.home()
ONEDRIVE = HOME / "OneDrive"

WATCH_FOLDERS = [
    Path("monitored_folder")
]

# Desktop
if (ONEDRIVE / "Desktop").exists():
    WATCH_FOLDERS.append(ONEDRIVE / "Desktop")
else:
    WATCH_FOLDERS.append(HOME / "Desktop")

# Documents
if (ONEDRIVE / "Documents").exists():
    WATCH_FOLDERS.append(ONEDRIVE / "Documents")
else:
    WATCH_FOLDERS.append(HOME / "Documents")

# Downloads
if (ONEDRIVE / "Downloads").exists():
    WATCH_FOLDERS.append(ONEDRIVE / "Downloads")
else:
    WATCH_FOLDERS.append(HOME / "Downloads")


# ==========================================================
# File Event Handler
# ==========================================================

class FileHandler(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if not file_path.exists():
            return

        if file_path.suffix == "":
            return

        print("\n======================================")
        print(f"New File Detected : {file_path.name}")
        print(f"Location          : {file_path.parent}")
        print("======================================")

        # Wait until file copy finishes
        time.sleep(1)

        try:

            result = classify_file(file_path)

            risk = result["risk"]
            score = result["score"]

            if risk == "Safe":

                print("Safe File")
                print(f"Risk Score : {score}")

                sha256 = calculate_sha256(file_path)

                # Prevent duplicate Safe entries
                exists = False

                for item in MetadataManager.all():

                    if (
                        item["sha256"] == sha256
                        and item["risk"] == "Safe"
                    ):
                        exists = True
                        break

                if not exists:

                    MetadataManager.add(

                        original_path=file_path,

                        stored_name="",

                        sha256=sha256,

                        risk="Safe",

                        risk_score=score

                    )

                print("Metadata Updated")

            else:

                print(f"Threat Detected ({risk})")
                print(f"Risk Score : {score}")

                quarantine_file(

                    file_path,

                    risk,

                    score

                )

        except Exception as e:

            print("\nError while scanning file")
            print(e)


# ==========================================================
# Start Monitoring
# ==========================================================

def start_monitor():

    if not WATCHDOG_AVAILABLE:
        print(
            "Watchdog is not installed; file monitoring is disabled."
        )
        return

    observer = Observer()

    print("\n======================================")
    print("AI-Assisted IT Disaster Recovery System")
    print("======================================")

    for folder in WATCH_FOLDERS:

        try:

            folder.mkdir(parents=True, exist_ok=True)

            observer.schedule(

                FileHandler(),

                str(folder),

                recursive=True

            )

            print(f"Monitoring : {folder}")

        except Exception as e:

            print(f"Unable to monitor : {folder}")
            print(e)

    observer.start()

    print("\nSystem Monitoring Active...\n")

    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        observer.stop()

    observer.join()