import joblib
import pandas as pd

from metrics_collector import get_system_metrics

MODEL_PATH = "system_prediction/models/failure_model.pkl"

# Load trained model
model = joblib.load(MODEL_PATH)

# Get live metrics
metrics = get_system_metrics()

# Create DataFrame with the same feature names used during training
features = pd.DataFrame([{
    "CPU": metrics["CPU"],
    "Memory": metrics["Memory"],
    "Disk": metrics["Disk"],
    "Network": metrics["Network"],
    "Processes": metrics["Processes"]
}])

prediction = model.predict(features)[0]
probability = model.predict_proba(features)[0][1]

print("\n========== CURRENT SYSTEM METRICS ==========")

for key, value in metrics.items():
    print(f"{key:<12}: {value}")

print("\n========== FAILURE PREDICTION ==========")

if prediction == 1:
    print("⚠️  FAILURE LIKELY")
else:
    print("✅ SYSTEM HEALTHY")

print(f"Failure Probability : {probability*100:.2f}%")