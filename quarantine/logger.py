import logging
from pathlib import Path

LOG_FILE = Path("secure_repository/logs/quarantine.log")

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def log_event(message):
    logging.info(message)