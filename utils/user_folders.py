import os


def get_user_folders():

    folders = []

    home = os.path.expanduser("~")

    # Local folders
    possible_folders = [

        os.path.join(home, "Desktop"),
        os.path.join(home, "Downloads"),
        os.path.join(home, "Documents"),
        os.path.join(home, "Pictures"),

        # OneDrive folders
        os.path.join(home, "OneDrive", "Desktop"),
        os.path.join(home, "OneDrive", "Documents"),
        os.path.join(home, "OneDrive", "Pictures")
    ]

    for folder in possible_folders:

        if os.path.exists(folder):
            folders.append(folder)

    return folders


if __name__ == "__main__":

    print(get_user_folders())