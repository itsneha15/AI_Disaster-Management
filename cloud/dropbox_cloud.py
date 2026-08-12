# cloud/dropbox_cloud.py

import os
try:
    import dropbox
    from dropbox.files import WriteMode
    DROPBOX_AVAILABLE = True
except ImportError:  # pragma: no cover
    dropbox = None
    WriteMode = None
    DROPBOX_AVAILABLE = False
from config import DROPBOX_TOKEN, DROPBOX_FOLDER
from logger import log_success, log_error, log_warning

class DropboxCloud:

    def __init__(self):
        self.dbx = None

    def connect(self):
        if not DROPBOX_AVAILABLE:
            log_warning(
                "Dropbox SDK is unavailable; cloud backup is disabled."
            )
            return False

        try:
            self.dbx = dropbox.Dropbox(DROPBOX_TOKEN)
            self.dbx.users_get_current_account()
            log_success("Dropbox connected!")
            return True

        except Exception as e:
            log_error(f"Dropbox failed: {e}")
            return False

    def upload(self, file_path, filename):
        if not DROPBOX_AVAILABLE or self.dbx is None or WriteMode is None:
            return False

        try:
            dropbox_path = f"{DROPBOX_FOLDER}{filename}"
            with open(file_path, 'rb') as f:
                self.dbx.files_upload(
                    f.read(),
                    dropbox_path,
                    mode=WriteMode.overwrite
                )
            log_success(f"Dropbox upload: {filename}")
            return True

        except Exception as e:
            log_error(f"Dropbox upload failed: {e}")
            return False

    def download_latest(self, download_path):
        if not DROPBOX_AVAILABLE or self.dbx is None:
            return False

        try:
            result = self.dbx.files_list_folder(
                DROPBOX_FOLDER
            )
            if not result.entries:
                return False

            latest = sorted(
                result.entries,
                key=lambda x: x.client_modified,
                reverse=True
            )[0]

            filepath = os.path.join(
                download_path, latest.name
            )
            self.dbx.files_download_to_file(
                filepath,
                latest.path_lower
            )

            log_success(f"Dropbox download: {latest.name}")
            return filepath

        except Exception as e:
            log_error(f"Dropbox download failed: {e}")
            return False