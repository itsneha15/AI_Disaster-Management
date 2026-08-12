import os


def is_accessible(path):

    try:

        os.listdir(path)

        return True

    except PermissionError:

        return False

    except Exception:

        return False