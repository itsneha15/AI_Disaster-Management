import math
import os
import pefile


def calculate_entropy(data):
    """
    Calculate Shannon entropy of file data.
    """

    if not data:
        return 0

    entropy = 0

    for x in range(256):

        p = data.count(bytes([x])) / len(data)

        if p > 0:
            entropy -= p * math.log2(p)

    return round(entropy, 2)


def analyze_pe(file_path):

    result = {

        "score": 0,

        "reasons": []

    }

    try:

        pe = pefile.PE(file_path)

        # --------------------------
        # Number of Sections
        # --------------------------

        sections = pe.FILE_HEADER.NumberOfSections

        if sections < 3:

            result["score"] += 15

            result["reasons"].append(
                "Very few PE sections"
            )

        elif sections > 8:

            result["score"] += 10

            result["reasons"].append(
                "Too many PE sections"
            )

        # --------------------------
        # File Entropy
        # --------------------------

        with open(file_path, "rb") as file:

            data = file.read()

        entropy = calculate_entropy(data)

        if entropy > 7.2:

            result["score"] += 25

            result["reasons"].append(
                "High entropy (possibly packed)"
            )

        # --------------------------
        # Executable Size
        # --------------------------

        size = os.path.getsize(file_path)

        if size < 10240:

            result["score"] += 15

            result["reasons"].append(
                "Very small executable"
            )

        elif size > 100 * 1024 * 1024:

            result["score"] += 10

            result["reasons"].append(
                "Very large executable"
            )

        # --------------------------
        # Writable + Executable Sections
        # --------------------------

        for section in pe.sections:

            flags = section.Characteristics

            executable = flags & 0x20000000
            writable = flags & 0x80000000

            if executable and writable:

                result["score"] += 20

                result["reasons"].append(
                    "Writable executable section"
                )

                break

        # --------------------------
        # Suspicious Section Names
        # --------------------------

        suspicious = [

            b".upx",
            b"UPX0",
            b"UPX1",
            b".aspack"

        ]

        for section in pe.sections:

            if section.Name.strip(b"\x00") in suspicious:

                result["score"] += 20

                result["reasons"].append(
                    "Packed executable section"
                )

                break

        # No suspicious indicators found
        if result["score"] == 0:
            result["reasons"].append("No suspicious indicators found")

        return result

    except Exception:

        return {

            "score": 0,

            "reasons": ["Not a valid PE"]

        }