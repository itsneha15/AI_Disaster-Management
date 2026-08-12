from utils.helpers import calculate_sha256


# Add known malware hashes here
KNOWN_MALWARE_HASHES = {

    # Example
    # "abcd123456..." : "Trojan",

}


def check_hash(file_path):
    """
    Compare SHA256 hash with known malware hashes.
    """

    sha256 = calculate_sha256(file_path)

    if sha256 is None:
        return "Unknown", None

    if sha256 in KNOWN_MALWARE_HASHES:
        return "Malicious", sha256

    return "Unknown", sha256