import os

from tqdm import tqdm

from config import SKIP_FOLDERS

from utils.user_folders import get_user_folders

from scanner.file_scanner import scan_file


def full_scan():

    # drives = get_available_drives()
    # drives = [r"C:\TestFolder2"]
    drives = get_user_folders()

    print()

    print("Detected Drives")

    print(drives)

    print()

    for drive in drives:

        print("=" * 60)

        print("Scanning:", drive)

        print("=" * 60)

        for root, dirs, files in os.walk(
            drive,
            topdown=True
        ):

            # Skip protected folders
            dirs[:] = [

                d

                for d in dirs

                if d not in SKIP_FOLDERS

            ]

            for file in tqdm(
                files,
                leave=False
            ):

                path = os.path.join(root, file)

                try:

                    scan_file(path)

                except Exception:

                    continue