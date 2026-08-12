import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

DATASET = "system_prediction/dataset/system_metrics.csv"
MODEL_DIR = "system_prediction/models"
MODEL_PATH = os.path.join(MODEL_DIR, "failure_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

# Load dataset
df = pd.read_csv(DATASET)

# Features and target
X = df[["CPU", "Memory", "Disk", "Network", "Processes"]]
y = df["Failure"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
print("\nAccuracy:", accuracy_score(y_test, y_pred))

print("\nClassification Report")
print(classification_report(y_test, y_pred))

print("Confusion Matrix")
print(confusion_matrix(y_test, y_pred))

# Save model
joblib.dump(model, MODEL_PATH)

print("\nModel saved to:", MODEL_PATH)