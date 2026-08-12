from detection.hash_checker import check_hash
from detection.extension_checker import check_extension
from detection.ember_detector import predict_file
from detection.heuristic_checker import analyze_pe


def analyze_file(file_path):

    hash_status, sha256 = check_hash(file_path)

    if hash_status == "Malicious":

        return {

            "status": "Malicious",

            "method": "Hash Database",

            "confidence": 100,

            "risk": "Critical",

            "sha256": sha256

        }

    extension = check_extension(file_path)

    if extension == "PE":

        prediction, confidence = predict_file(file_path)

        heuristic = analyze_pe(file_path)

        score = heuristic["score"]

        reasons = heuristic["reasons"]

        # Final decision
        if prediction == "Malicious":

            final_status = "Malicious"
            risk = "Critical"

        else:

            if score >= 60:

                final_status = "Suspicious"
                risk = "Critical"

            elif score >= 40:

                final_status = "Suspicious"
                risk = "High"

            elif score >= 20:

                final_status = "Suspicious"
                risk = "Medium"

            else:

                final_status = "Safe"
                risk = "Low"

        return {

            "status": final_status,

            "method": "LightGBM + Heuristics",

            "confidence": confidence,

            "risk": risk,

            "heuristic_score": score,

            "reasons": reasons,

            "sha256": sha256

        }

        prediction, confidence = predict_file(file_path)

        heuristic = analyze_pe(file_path)

        score = heuristic["score"]

        reasons = heuristic["reasons"]

        # Determine risk based on heuristic score
        if score >= 60:
            risk = "Critical"
        elif score >= 40:
            risk = "High"
        elif score >= 20:
            risk = "Medium"
        else:
            risk = "Low"

        return {

            "status": prediction,

            "method": "LightGBM + Heuristics",

            "confidence": confidence,

            "risk": risk,

            "heuristic_score": score,

            "reasons": reasons,

            "sha256": sha256

        }

    elif extension == "SCRIPT":

        return {

            "status": "Suspicious",

            "method": "Script Detection",

            "confidence": 80,

            "risk": "High",

            "sha256": sha256

        }

    elif extension == "OFFICE":

        return {

            "status": "Safe",

            "method": "Office Document",

            "confidence": 100,

            "risk": "Medium",

            "sha256": sha256

        }

    elif extension == "PDF":

        return {

            "status": "Safe",

            "method": "PDF",

            "confidence": 100,

            "risk": "Low",

            "sha256": sha256

        }

    elif extension == "TEXT":

        return {

            "status": "Safe",

            "method": "Text",

            "confidence": 100,

            "risk": "Very Low",

            "sha256": sha256

        }

    return {

        "status": "Ignored",

        "method": "Unknown",

        "confidence": 0,

        "risk": "Unknown",

        "sha256": sha256

    }