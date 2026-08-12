# config.py - COMPLETE MERGED VERSION

import os

# ==========================
# Project Root
# ==========================

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = BASE_DIR

# ==========================
# Existing Project Settings
# ==========================

# Model (your existing)
MODEL_PATH = os.path.join(
    BASE_DIR, "models", "ember_model.pkl"
)

# Reports (your existing)
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")
CSV_REPORT    = os.path.join(REPORT_FOLDER, "reports.csv")
JSON_REPORT   = os.path.join(REPORT_FOLDER, "reports.json")

# Logs (your existing)
LOG_FOLDER = os.path.join(BASE_DIR, "logs")
LOG_FILE   = os.path.join(LOG_FOLDER, "scanner.log")

# Quarantine (your existing)
QUARANTINE_FOLDER = os.path.join(
    BASE_DIR, "quarantine_storage"
)

# File Extensions (your existing)
PE_EXTENSIONS = [
    ".exe", ".dll", ".sys", ".scr", ".ocx"
]

DANGEROUS_EXTENSIONS = [
    ".bat", ".cmd", ".ps1", ".vbs", ".js"
]

SKIP_FOLDERS = [
    "Windows", "Program Files",
    "Program Files (x86)", "ProgramData",
    "$Recycle.Bin", "System Volume Information",
    "Recovery", "AppData", ".git", ".vscode",
    ".idea", "node_modules", "__pycache__"
]

SCAN_EXTENSIONS = [
    ".exe", ".dll", ".sys", ".scr", ".ocx",
    ".bat", ".cmd", ".ps1", ".vbs", ".js",
    ".doc", ".docx", ".xls", ".xlsx",
    ".ppt", ".pptx", ".pdf",
    ".zip", ".rar", ".7z", ".txt"
]

SCRIPT_EXTENSIONS = [
    ".bat", ".cmd", ".ps1", ".vbs", ".js"
]

OFFICE_EXTENSIONS = [
    ".doc", ".docx", ".xls",
    ".xlsx", ".ppt", ".pptx"
]

PDF_EXTENSIONS  = [".pdf"]
TEXT_EXTENSIONS = [".txt"]

# ==========================
# New Backup Project Settings
# ==========================

# Monitoring thresholds
CPU_THRESHOLD    = 40
MEMORY_THRESHOLD = 86
DISK_THRESHOLD   = 60

# Intervals
CHECK_INTERVAL_SECONDS = 5
BACKUP_INTERVAL_HOURS  = 1

# New folder paths
CRITICAL_DATA_PATH = os.path.join(
    BASE_DIR, "critical_data"
)
LOCAL_BACKUP_PATH  = os.path.join(
    BASE_DIR, "storage", "local_backup"
)
QUARANTINE_PATH    = os.path.join(
    BASE_DIR, "storage", "quarantine"
)
NEW_LOG_PATH       = os.path.join(
    BASE_DIR, "storage", "logs"
)

# Both names work now
MODELS_PATH = os.path.join(BASE_DIR, "models")

# Google Drive
GDRIVE_CREDENTIALS = os.path.join(
    BASE_DIR, "credentials.json"
)
GDRIVE_TOKEN  = os.path.join(BASE_DIR, "token.json")
GDRIVE_FOLDER = "AI_DR_Backups"

# ==========================
# OneDrive
# ==========================

ONEDRIVE_CLIENT_ID = os.getenv(
    "ONEDRIVE_CLIENT_ID"
)

ONEDRIVE_SCOPES = [
    "Files.ReadWrite",
    "User.Read"
]

# ==========================
# Dropbox
# ==========================

DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
DROPBOX_FOLDER = os.getenv(
    "DROPBOX_FOLDER",
    "/AI_DR_Backups/"
)