# backup/backup_manager.py

import os
import time
import zipfile
from datetime import datetime
from cloud.gdrive        import GoogleDriveCloud
from cloud.onedrive      import OneDriveCloud
from cloud.dropbox_cloud import DropboxCloud
from config import CRITICAL_DATA_PATH, LOCAL_BACKUP_PATH
from logger import log_info, log_error, log_success, log_warning

class BackupManager:

    def __init__(self):
        os.makedirs(LOCAL_BACKUP_PATH,  exist_ok=True)
        os.makedirs(CRITICAL_DATA_PATH, exist_ok=True)

        log_info("Connecting to clouds...")

        # Each cloud is connected independently. A bad credential/token
        # for one provider must NOT prevent the others (or local backup,
        # which never depends on the cloud at all) from working.
        self.gdrive      = GoogleDriveCloud()
        self.onedrive    = OneDriveCloud()
        self.dropbox     = DropboxCloud()

        self.gdrive_ok   = self._safe_connect(
            "Google Drive", self.gdrive
        )
        self.onedrive_ok = self._safe_connect(
            "OneDrive", self.onedrive
        )
        self.dropbox_ok  = self._safe_connect(
            "Dropbox", self.dropbox
        )

        log_info(
            f"Cloud status -> "
            f"Google Drive: {self.gdrive_ok}, "
            f"OneDrive: {self.onedrive_ok}, "
            f"Dropbox: {self.dropbox_ok}"
        )

    def _safe_connect(self, name, client):
        try:
            return bool(client.connect())
        except Exception as e:
            log_warning(f"{name} connect failed: {e}")
            return False

    def create_backup(self, reason="Scheduled"):

        # Start timer
        start_time = time.time()
        start_str  = datetime.now().strftime("%H:%M:%S")

        log_info(f"Backup started: {reason}")
        print(f"\n⏱ Backup started at: {start_str}")

        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        local_path  = os.path.join(
            LOCAL_BACKUP_PATH, backup_name
        )

        # Create zip
        try:
            file_count = 0
            with zipfile.ZipFile(
                local_path, 'w', zipfile.ZIP_DEFLATED
            ) as zipf:
                for root, dirs, files in os.walk(
                    CRITICAL_DATA_PATH
                ):
                    for file in files:
                        file_path = os.path.join(root, file)

                        # Store each entry RELATIVE to CRITICAL_DATA_PATH,
                        # not as an absolute path. Without this, the zip
                        # stores full paths like "C:\Users\...\critical_data\
                        # file.txt" as the entry name, which many zip
                        # tools (including Windows Explorer's built-in
                        # extractor) fail to open cleanly.
                        arcname = os.path.relpath(
                            file_path, CRITICAL_DATA_PATH
                        )
                        zipf.write(file_path, arcname)
                        file_count += 1

            if file_count == 0:
                log_warning(
                    "Backup zip created but CRITICAL_DATA_PATH was "
                    "empty - nothing was actually backed up."
                )
            log_success(
                f"Local backup: {backup_name} ({file_count} files)"
            )

        except Exception as e:
            log_error(f"Local backup failed: {e}")
            return False

        # Upload to all clouds - each wrapped so one provider failing
        # mid-upload doesn't stop the others or crash create_backup().
        results = {
            'Local'        : True,
            'Google Drive' : False,
            'OneDrive'     : False,
            'Dropbox'      : False
        }

        if self.gdrive_ok:
            try:
                results['Google Drive'] = self.gdrive.upload(
                    local_path, backup_name
                )
            except Exception as e:
                log_warning(f"Google Drive upload failed: {e}")

        if self.onedrive_ok:
            try:
                results['OneDrive'] = self.onedrive.upload(
                    local_path, backup_name
                )
            except Exception as e:
                log_warning(f"OneDrive upload failed: {e}")

        if self.dropbox_ok:
            try:
                results['Dropbox'] = self.dropbox.upload(
                    local_path, backup_name
                )
            except Exception as e:
                log_warning(f"Dropbox upload failed: {e}")

        # End timer
        elapsed = round(time.time() - start_time, 2)
        end_str = datetime.now().strftime("%H:%M:%S")

        # Print summary
        print("\n========== BACKUP SUMMARY ==========")
        print(f"Backup  : {backup_name}")
        print(f"Reason  : {reason}")
        print(f"Files   : {file_count}")
        for cloud, status in results.items():
            icon = '✅' if status else '❌'
            print(f"{icon} {cloud}")
        print(f"\n⏱ Started  : {start_str}")
        print(f"⏱ Finished : {end_str}")
        print(f"⏱ Duration : {elapsed} seconds")
        print("=====================================\n")

        log_success(f"Backup done in {elapsed} seconds")
        return True