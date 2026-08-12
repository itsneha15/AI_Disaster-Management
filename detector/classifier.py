from detector.extension_checker import check_extension
from detector.filename_checker import check_filename
from detector.hash_checker import check_hash
from detector.size_checker import check_size
from detector.decision_engine import decide


def classify_file(file_path):

    extension_score = check_extension(file_path)
    filename_score = check_filename(file_path)
    hash_score = check_hash(file_path)
    size_score = check_size(file_path)

    total_score = (
        extension_score
        + filename_score
        + hash_score
        + size_score
    )

    risk = decide(total_score)


    return {
        "risk": risk,
        "score": total_score
    }