# backup/recovery_engine.py

import os
import time
import zipfile
import shutil
from datetime import datetime
from config import CRITICAL_DATA_PATH, LOCAL_BACKUP_PATH
from logger import log_warning, log_error, log_success

class RecoveryEngine:

    def __init__(self, gdrive, onedrive, dropbox):
        self.gdrive   = gdrive
        self.onedrive = onedrive
        self.dropbox  = dropbox

    def restore(self, reason="Manual"):

        # Start timer
        start_time = time.time()
        start_str  = datetime.now().strftime("%H:%M:%S")

        log_warning(f"Recovery started: {reason}")
        print(f"\n⏱ Recovery started at: {start_str}")
        print("\n========== RECOVERY STARTED ==========")

        sources = [
            ("Local Backup", self.restore_from_local),
            ("Google Drive", self.restore_from_gdrive),
            ("OneDrive",     self.restore_from_onedrive),
            ("Dropbox",      self.restore_from_dropbox)
        ]

        for name, func in sources:
            print(f"Trying {name}...")
            try:
                if func():
                    elapsed = round(
                        time.time() - start_time, 2
                    )
                    end_str = datetime.now().strftime(
                        "%H:%M:%S"
                    )

                    print(f"✅ Restored from {name}!")
                    print(f"\n⏱ Started  : {start_str}")
                    print(f"⏱ Finished : {end_str}")
                    print(f"⏱ RTO      : {elapsed} seconds")
                    print("======================================\n")

                    log_success(
                        f"Recovered from {name} "
                        f"in {elapsed} seconds"
                    )
                    return True

            except Exception as e:
                print(f"❌ {name} failed, trying next...")
                continue

        log_error("All recovery sources failed!")
        return False

    def restore_from_local(self):
        backups = sorted([
            f for f in os.listdir(LOCAL_BACKUP_PATH)
            if f.endswith('.zip')
        ])
        if not backups:
            return False
        self.extract(
            os.path.join(LOCAL_BACKUP_PATH, backups[-1])
        )
        return True

    def restore_from_gdrive(self):
        path = self.gdrive.download_latest(LOCAL_BACKUP_PATH)
        if path:
            self.extract(path)
            return True
        return False

    def restore_from_onedrive(self):
        path = self.onedrive.download_latest(LOCAL_BACKUP_PATH)
        if path:
            self.extract(path)
            return True
        return False

    def restore_from_dropbox(self):
        path = self.dropbox.download_latest(LOCAL_BACKUP_PATH)
        if path:
            self.extract(path)
            return True
        return False

    def extract(self, zip_path):
        if os.path.exists(CRITICAL_DATA_PATH):
            shutil.rmtree(CRITICAL_DATA_PATH)
        os.makedirs(CRITICAL_DATA_PATH)

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(CRITICAL_DATA_PATH)

        log_success("Files restored!")