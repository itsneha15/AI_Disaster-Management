import json
import os
import bcrypt
from pathlib import Path


# =========================================================
# LOCAL ADMIN FILE
# =========================================================

ADMIN_FILE = Path("config/admin.json")


def authenticate(username, password):
    """
    Authenticate an administrator.

    Local development:
        Uses config/admin.json

    Vercel / production:
        Uses ADMIN_USERNAME and ADMIN_PASSWORD_HASH
        environment variables.
    """

    # =====================================================
    # VERCEL / ENVIRONMENT VARIABLE AUTHENTICATION
    # =====================================================

    env_username = os.getenv("ADMIN_USERNAME")
    env_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

    if env_username and env_password_hash:

        # Check username
        if username != env_username:
            return False

        # Check bcrypt password hash
        try:

            return bcrypt.checkpw(
                password.encode("utf-8"),
                env_password_hash.encode("utf-8")
            )

        except (ValueError, TypeError):

            print(
                "Invalid ADMIN_PASSWORD_HASH."
            )

            return False


    # =====================================================
    # LOCAL ADMIN FILE AUTHENTICATION
    # =====================================================

    if not ADMIN_FILE.exists():

        return False


    try:

        with open(
            ADMIN_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            admin = json.load(f)

    except (OSError, json.JSONDecodeError):

        return False


    # =====================================================
    # USERNAME
    # =====================================================

    if username != admin.get("username"):

        return False


    # =====================================================
    # PASSWORD
    # =====================================================

    stored_hash = admin.get(
        "password",
        ""
    )


    try:

        return bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )

    except (ValueError, TypeError):

        print(
            "Invalid bcrypt hash found "
            "in admin.json"
        )

        return False