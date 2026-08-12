from pathlib import Path
from datetime import datetime
import os


# ---------------------------------------------------------
# Runtime log location
# ---------------------------------------------------------
#
# Vercel's deployed filesystem is read-only.
# /tmp is the writable temporary directory available
# during a serverless function execution.
#
# Locally we continue using secure_repository/logs.
#

if os.getenv("VERCEL"):
    LOG_FILE = Path("/tmp/ai_disaster_quarantine.log")
else:
    LOG_FILE = Path("secure_repository/logs/quarantine.log")


def log_event(message):
    """
    Write a quarantine event to the runtime log.
    """

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    try:
        LOG_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(
                f"[{timestamp}] {message}\n"
            )

    except Exception as error:
        print(
            f"Warning: Could not write quarantine log: {error}"
        )


def get_log_file():
    """
    Return the current runtime log path.
    """

    return LOG_FILE