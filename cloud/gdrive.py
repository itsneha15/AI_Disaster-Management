# cloud/gdrive.py

import os
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.http import MediaIoBaseDownload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    GOOGLE_API_AVAILABLE = True
except ImportError:  # pragma: no cover
    build = None
    MediaFileUpload = None
    MediaIoBaseDownload = None
    InstalledAppFlow = None
    Request = None
    Credentials = None
    GOOGLE_API_AVAILABLE = False
from config import GDRIVE_CREDENTIALS, GDRIVE_TOKEN
from config import GDRIVE_FOLDER
from logger import log_success, log_error, log_warning

SCOPES = ['https://www.googleapis.com/auth/drive']

class GoogleDriveCloud:

    def __init__(self):
        self.service   = None
        self.folder_id = None

    def connect(self):
        if not GOOGLE_API_AVAILABLE:
            log_warning(
                "Google Drive SDK is unavailable; cloud backup is disabled."
            )
            return False

        try:
            creds = None

            if os.path.exists(GDRIVE_TOKEN):
                creds = Credentials.from_authorized_user_file(
                    GDRIVE_TOKEN, SCOPES
                )

            if not creds or not creds.valid:
                if creds and creds.expired:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        GDRIVE_CREDENTIALS, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                with open(GDRIVE_TOKEN, 'w') as t:
                    t.write(creds.to_json())

            self.service   = build(
                'drive', 'v3', credentials=creds
            )
            self.folder_id = self.get_or_create_folder()
            log_success("Google Drive connected!")
            return True

        except Exception as e:
            log_error(f"Google Drive failed: {e}")
            return False

    def get_or_create_folder(self):
        results = self.service.files().list(
            q=f"name='{GDRIVE_FOLDER}' and "
              f"mimeType='application/vnd.google-apps.folder'",
            fields="files(id)"
        ).execute()

        files = results.get('files', [])
        if files:
            return files[0]['id']

        folder = self.service.files().create(
            body={
                'name'    : GDRIVE_FOLDER,
                'mimeType': 'application/vnd.google-apps.folder'
            }
        ).execute()
        return folder['id']

    def upload(self, file_path, filename):
        if self.service is None or MediaFileUpload is None:
            return False

        try:
            media = MediaFileUpload(file_path, resumable=True)
            self.service.files().create(
                body={
                    'name'   : filename,
                    'parents': [self.folder_id]
                },
                media_body=media,
                fields='id'
            ).execute()
            log_success(f"GDrive upload: {filename}")
            return True

        except Exception as e:
            log_error(f"GDrive upload failed: {e}")
            return False

    def download_latest(self, download_path):
        if self.service is None or MediaIoBaseDownload is None:
            return False

        try:
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents and "
                  f"name contains 'backup_'",
                orderBy="createdTime desc",
                pageSize=1,
                fields="files(id, name)"
            ).execute()

            files = results.get('files', [])
            if not files:
                return False

            latest   = files[0]
            filepath = os.path.join(
                download_path, latest['name']
            )
            request  = self.service.files().get_media(
                fileId=latest['id']
            )

            with open(filepath, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()

            log_success(f"GDrive download: {latest['name']}")
            return filepath

        except Exception as e:
            log_error(f"GDrive download failed: {e}")
            return False