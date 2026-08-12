import os
import random
import pandas as pd
from metrics_collector import get_system_metrics

DATASET_PATH = "system_prediction/dataset/system_metrics.csv"

os.makedirs("system_prediction/dataset", exist_ok=True)

records = []

print("Collecting dataset...")

for i in range(1000):

    metrics = get_system_metrics()

    # Generate realistic variations
    cpu = max(0, min(metrics["CPU"] + random.uniform(-25, 25), 100))
    memory = max(0, min(metrics["Memory"] + random.uniform(-20, 20), 100))
    disk = max(0, min(metrics["Disk"] + random.uniform(-10, 10), 100))
    network = max(0, min(metrics["Network"] + random.uniform(0, 40), 100))
    processes = max(50, metrics["Processes"] + random.randint(-50, 80))

    # More realistic failure score
    risk_score = 0

    if cpu > 85:
        risk_score += 2

    if memory > 85:
        risk_score += 2

    if disk > 90:
        risk_score += 2

    if network > 70:
        risk_score += 1

    if processes > 300:
        risk_score += 1

    if cpu > 75 and memory > 80:
        risk_score += 2

    if cpu > 80 and processes > 280:
        risk_score += 1

    # Final label
    failure = 1 if risk_score >= 3 else 0

    records.append([
        round(cpu, 2),
        round(memory, 2),
        round(disk, 2),
        round(network, 2),
        processes,
        failure
    ])

df = pd.DataFrame(
    records,
    columns=[
        "CPU",
        "Memory",
        "Disk",
        "Network",
        "Processes",
        "Failure"
    ]
)

df.to_csv(DATASET_PATH, index=False)

print(df.head())

print("\nDataset Shape:", df.shape)

print("\nFailure Distribution")
print(df["Failure"].value_counts())