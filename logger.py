import os
import logging
from datetime import datetime
from config import LOG_FOLDER


# ============================================================
# VERCEL / LOCAL LOG DIRECTORY
# ============================================================

if os.getenv("VERCEL") == "1":
    # Vercel's deployed filesystem is read-only.
    # /tmp is the writable temporary directory.
    LOG_DIR = "/tmp"
else:
    # Local development
    LOG_DIR = LOG_FOLDER


os.makedirs(LOG_DIR, exist_ok=True)


# ============================================================
# LOG FILE
# ============================================================

log_file = os.path.join(
    LOG_DIR,
    f"system_{datetime.now().strftime('%Y%m%d')}.log"
)


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)


logger = logging.getLogger("AI_DR")


# ============================================================
# LOGGER FUNCTIONS
# ============================================================

def log_info(msg):
    logger.info(msg)


def log_warning(msg):
    logger.warning(msg)


def log_error(msg):
    logger.error(msg)


def log_success(msg):
    logger.info(f"SUCCESS: {msg}")