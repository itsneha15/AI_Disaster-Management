import os

from config import (
    PE_EXTENSIONS,
    SCRIPT_EXTENSIONS,
    OFFICE_EXTENSIONS,
    PDF_EXTENSIONS,
    TEXT_EXTENSIONS
)


def check_extension(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension in PE_EXTENSIONS:
        return "PE"

    elif extension in SCRIPT_EXTENSIONS:
        return "SCRIPT"

    elif extension in OFFICE_EXTENSIONS:
        return "OFFICE"

    elif extension in PDF_EXTENSIONS:
        return "PDF"

    elif extension in TEXT_EXTENSIONS:
        return "TEXT"

    return "OTHER"