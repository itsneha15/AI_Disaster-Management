import time
import os
import joblib
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metrics_collector import get_system_metrics

from alert.alert_manager import generate_alert, resolve_alert
from alert.notifier import display_alert

MODEL_PATH = "system_prediction/models/failure_model.pkl"

model = joblib.load(MODEL_PATH)

while True:

    metrics = get_system_metrics()
    SIMULATION_MODE = False

    # Simulate a failure scenario
    if SIMULATION_MODE:
        metrics["CPU"] = 98
        metrics["Memory"] = 97
        metrics["Disk"] = 98
        metrics["Network"] = 90
        metrics["Processes"] = 400

    features = pd.DataFrame([{
        "CPU": metrics["CPU"],
        "Memory": metrics["Memory"],
        "Disk": metrics["Disk"],
        "Network": metrics["Network"],
        "Processes": metrics["Processes"]
    }])

    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    # Health Score (0-100)
    health_score = round((1 - probability) * 100, 2)

    os.system("cls" if os.name == "nt" else "clear")

    print("=" * 50)
    print("      AI FAILURE PREDICTION MONITOR")
    print("=" * 50)

    print(f"CPU        : {metrics['CPU']} %")
    print(f"Memory     : {metrics['Memory']} %")
    print(f"Disk       : {metrics['Disk']} %")
    print(f"Network    : {metrics['Network']} %")
    print(f"Processes  : {metrics['Processes']}")

    print("\n" + "-" * 50)

    if prediction == 1:

        status = "⚠️ FAILURE LIKELY"

        # Decide severity
        if probability >= 0.80:
            severity = "Critical"
        elif probability >= 0.60:
            severity = "High"
        else:
            severity = "Medium"

        alert = generate_alert(

            alert_type="System Failure",

            severity=severity,

            message="AI model predicts a possible system failure.",

            probability=round(probability * 100, 2),

            action="Notify administrator and trigger backup."

        )

        display_alert(alert)

    else:

        status = "✅ SYSTEM HEALTHY"

        resolve_alert("System Failure")

    print(f"Status              : {status}")
    print(f"Failure Probability : {probability*100:.2f}%")
    print(f"System Health Score : {health_score:.2f}%")

    print("\nRefreshing in 5 seconds...")
    time.sleep(5)