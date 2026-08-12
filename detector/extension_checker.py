from pathlib import Path

EXTENSIONS = {

    ".exe":40,

    ".bat":40,

    ".cmd":35,

    ".dll":35,

    ".vbs":35,

    ".ps1":35,

    ".scr":40,

    ".js":20,

    ".jar":20

}


def check_extension(file_path):

    ext = Path(file_path).suffix.lower()

    return EXTENSIONS.get(ext,0)