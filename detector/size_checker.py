import os


def check_size(file_path):

    size = os.path.getsize(file_path)

    if size < 1024:
        return 10

    elif size > 100 * 1024 * 1024:
        return 20

    return 0