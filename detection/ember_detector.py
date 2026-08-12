import joblib

from config import MODEL_PATH
from scanner.feature_extraction import extract_features


# Load model only once
model = joblib.load(MODEL_PATH)


def predict_file(file_path):
    """
    Predict whether a PE file is safe or malicious.
    """

    features = extract_features(file_path)

    if features is None:
        return "Unknown", 0

    prediction = model.predict(features)[0]

    confidence = 0

    if hasattr(model, "predict_proba"):

        probabilities = model.predict_proba(features)[0]

        confidence = round(max(probabilities) * 100, 2)

    if prediction == 1:
        return "Malicious", confidence

    return "Safe", confidence