# modules/anomaly_detection.py
# Replace top imports with this:

import sys
import os

sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

try:
    from sklearn.ensemble import IsolationForest
except ImportError:  # pragma: no cover
    IsolationForest = None

from config import MODELS_PATH
from logger import log_warning, log_info, log_success

class AnomalyDetection:

    def __init__(self):
        if pd is None or np is None or IsolationForest is None:
            log_warning(
                "Anomaly detection dependencies are unavailable; "
                "anomaly checks are disabled."
            )
            self.model = None
            return

        try:
            df = pd.read_csv("system_dataset.csv")
            X  = df[["CPU", "Memory", "Disk"]]

            self.model = IsolationForest(
                contamination=0.05,
                random_state=42
            )
            self.model.fit(X)
            log_success("Anomaly model trained!")

        except Exception as e:
            log_warning(f"Anomaly model error: {e}")
            self.model = None

    def detect(self, metrics):
        if self.model is None:
            return "NORMAL"

        try:
            live_data = pd.DataFrame([{
                "CPU"    : metrics["cpu"],
                "Memory" : metrics["memory"],
                "Disk"   : metrics["disk"]
            }])

            result = self.model.predict(live_data)[0]

            if result == -1:
                print("⚠ WARNING: ANOMALY DETECTED!")
                return "ANOMALY"
            else:
                print("✅ System Behaviour Normal")
                return "NORMAL"

        except Exception as e:
            log_warning(f"Anomaly error: {e}")
            return "NORMAL"