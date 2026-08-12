import os

from config import SCAN_EXTENSIONS
from detection.decision_engine import analyze_file
from quarantine.quarantine_manager import quarantine_file
from reports.report_generator import save_report


def scan_file(file_path):

    # Check if it is a file
    if not os.path.isfile(file_path):
        return

    # Check extension
    extension = os.path.splitext(file_path)[1].lower()

    if extension not in SCAN_EXTENSIONS:
        return

    # Analyze the file
    result = analyze_file(file_path)

    report = {

        "file": file_path,

        "status": result["status"],

        "method": result["method"],

        "risk": result["risk"],

        "confidence": result["confidence"],

        "sha256": result["sha256"]

    }

    save_report(report)

    print("=" * 60)

    print("File       :", file_path)
    print("Status     :", result["status"])
    print("Risk Level :", result["risk"])
    print("Method     :", result["method"])
    print("Confidence :", result["confidence"])

    if "heuristic_score" in result:

        print("Heuristic Score :", result["heuristic_score"])

        if result["reasons"]:

            print("Reasons:")

            for reason in result["reasons"]:

                print("   -", reason)

    if result["sha256"]:
        print("SHA256     :", result["sha256"])

    if result["status"] == "Malicious":

        location = quarantine_file(file_path)

        print("\nMoved to Quarantine")
        print(location)