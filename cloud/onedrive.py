# cloud/onedrive.py

import os
try:
    import requests
except ImportError:  # pragma: no cover
    requests = None
try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:  # pragma: no cover
    msal = None
    MSAL_AVAILABLE = False
from config import ONEDRIVE_CLIENT_ID, BASE_DIR
from logger import log_success, log_error, log_info

# Use these scopes directly here
SCOPES = ["https://graph.microsoft.com/Files.ReadWrite",
          "https://graph.microsoft.com/User.Read"]

# Token cache is saved here so a successful login survives app restarts.
# Without this, MSAL's default cache is in-memory only and every restart
# forces a fresh interactive login - which blocks the app for up to
# 15 minutes if nobody's there to complete it.
CACHE_PATH = os.path.join(BASE_DIR, "onedrive_token_cache.bin")


class OneDriveCloud:

    def __init__(self):
        self.token    = None
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.cache    = msal.SerializableTokenCache() if MSAL_AVAILABLE else None

        if not MSAL_AVAILABLE:
            log_error("OneDrive SDK is unavailable; cloud backup is disabled.")
            return

        if os.path.exists(CACHE_PATH):
            try:
                with open(CACHE_PATH, "r") as f:
                    self.cache.deserialize(f.read())
            except Exception as e:
                log_error(f"OneDrive cache load failed: {e}")

    def _save_cache(self):
        if not MSAL_AVAILABLE:
            return

        if self.cache.has_state_changed:
            try:
                with open(CACHE_PATH, "w") as f:
                    f.write(self.cache.serialize())
            except Exception as e:
                log_error(f"OneDrive cache save failed: {e}")

    def connect(self):
        if not MSAL_AVAILABLE:
            return False

        try:
            log_info("Connecting to OneDrive...")

            app = msal.PublicClientApplication(
                ONEDRIVE_CLIENT_ID,
                authority="https://login.microsoftonline.com/common",
                token_cache=self.cache
            )

            # Try silent first
            accounts = app.get_accounts()
            result   = None

            if accounts:
                log_info("Trying silent OneDrive login...")
                result = app.acquire_token_silent(
                    SCOPES,
                    account=accounts[0]
                )

            # If silent fails do device flow
            if not result:
                log_info("Starting OneDrive device flow...")

                flow = app.initiate_device_flow(
                    scopes=SCOPES
                )

                # Check flow worked
                if "user_code" not in flow:
                    log_error(
                        f"OneDrive flow error: "
                        f"{flow.get('error_description', 'Unknown')}"
                    )
                    return False

                # Show login instructions
                print("\n" + "="*50)
                print("ONEDRIVE LOGIN REQUIRED")
                print("="*50)
                print(f"1. Open browser")
                print(f"2. Go to: https://microsoft.com/devicelogin")
                print(f"3. Enter code: {flow['user_code']}")
                print(f"4. Login with your Outlook account")
                print("="*50 + "\n")

                result = app.acquire_token_by_device_flow(flow)

            self._save_cache()

            if result and "access_token" in result:
                self.token = result["access_token"]
                log_success("OneDrive connected!")
                return True

            error_desc = (
                result.get("error_description", "Unknown error")
                if result else "No result from MSAL"
            )
            log_error(f"OneDrive token failed: {error_desc}")
            return False

        except Exception as e:
            log_error(f"OneDrive error: {e}")
            return False

    def upload(self, file_path, filename):
        if not MSAL_AVAILABLE or requests is None:
            return False

        try:
            if not self.token:
                return False

            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type' : 'application/octet-stream'
            }

            with open(file_path, 'rb') as f:
                response = requests.put(
                    f'{self.base_url}/me/drive/root:'
                    f'/AI_DR_Backups/{filename}:/content',
                    headers=headers,
                    data=f
                )

            if response.status_code in [200, 201]:
                log_success(f"OneDrive upload: {filename}")
                return True

            log_error(
                f"OneDrive upload failed: "
                f"{response.status_code}"
            )
            return False

        except Exception as e:
            log_error(f"OneDrive upload error: {e}")
            return False

    def download_latest(self, download_path):
        if not MSAL_AVAILABLE or requests is None:
            return False

        try:
            if not self.token:
                return False

            headers  = {
                'Authorization': f'Bearer {self.token}'
            }
            response = requests.get(
                f'{self.base_url}/me/drive/root:'
                f'/AI_DR_Backups:/children',
                headers=headers
            )

            files = response.json().get('value', [])
            if not files:
                return False

            latest = sorted(
                files,
                key=lambda x: x['lastModifiedDateTime'],
                reverse=True
            )[0]

            file_response = requests.get(
                latest['@microsoft.graph.downloadUrl']
            )

            filepath = os.path.join(
                download_path, latest['name']
            )
            with open(filepath, 'wb') as f:
                f.write(file_response.content)

            log_success(
                f"OneDrive download: {latest['name']}"
            )
            return filepath

        except Exception as e:
            log_error(f"OneDrive download failed: {e}")
            return False