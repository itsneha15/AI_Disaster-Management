import os


def get_available_drives():

    drives = []

    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":

        drive = f"{letter}:\\"

        if os.path.exists(drive):

            drives.append(drive)

    return drives


if __name__ == "__main__":

    drives = get_available_drives()

    print("Detected Drives:")

    for drive in drives:

        print(drive)