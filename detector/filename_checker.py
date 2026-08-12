from pathlib import Path

WORDS = [

    "virus",

    "trojan",

    "worm",

    "payload",

    "hack",

    "malware",

    "ransom"

]


def check_filename(file_path):

    score = 0

    name = Path(file_path).stem.lower()

    for word in WORDS:

        if word in name:

            score += 20

    return score