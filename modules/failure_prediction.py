# modules/failure_prediction.py
# UPDATED TO USE THEIR BETTER MODEL
# + manual threshold override for on-demand failure testing

import sys
import os

sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))

# Add system_prediction to path
sys.path.insert(0, os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ),
    'system_prediction'
))

try:
    import joblib
except ImportError:  # pragma: no cover
    joblib = None

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

try:
    from sklearn.ensemble import RandomForestClassifier
except ImportError:  # pragma: no cover
    RandomForestClassifier = None

try:
    from logger import (
        log_warning, log_info, log_success
    )
except:
    def log_info(m):    print(f"INFO: {m}")
    def log_warning(m): print(f"WARNING: {m}")
    def log_success(m): print(f"SUCCESS: {m}")

try:
    from config import (
        MODELS_PATH,
        CPU_THRESHOLD,
        MEMORY_THRESHOLD,
        DISK_THRESHOLD
    )
except:
    MODELS_PATH      = "models/"
    CPU_THRESHOLD    = 85
    MEMORY_THRESHOLD = 85
    DISK_THRESHOLD   = 90


class FailurePrediction:

    def __init__(self):
        self.last_probability = 0
        self.use_full_features = False
        self.model = None

        # Priority 1: Their 5-feature model
        their_model = os.path.join(
            "system_prediction",
            "models",
            "failure_model.pkl"
        )

        # Priority 2: Our basic model
        our_model = os.path.join(
            MODELS_PATH,
            "failure_model.pkl"
        )

        if os.path.exists(their_model):
            try:
                if joblib is None:
                    raise ImportError("joblib is not installed")
                self.model = joblib.load(their_model)
                self.use_full_features = True
                log_success(
                    "Loaded 5-feature failure model!"
                )
                return
            except Exception as e:
                log_warning(f"Their model failed: {e}")

        if os.path.exists(our_model):
            try:
                if joblib is None:
                    raise ImportError("joblib is not installed")
                self.model = joblib.load(our_model)
                self.use_full_features = False
                log_success(
                    "Loaded basic failure model!"
                )
                return
            except Exception as e:
                log_warning(f"Our model failed: {e}")

        # Train new model if none found
        log_info("No model found! Training new...")
        self.model = self._train_new_model()
        self.use_full_features = False

    def _train_new_model(self):
        if (
            joblib is None
            or pd is None
            or np is None
            or RandomForestClassifier is None
        ):
            log_warning(
                "ML dependencies are unavailable; using "
                "threshold-only failure detection."
            )
            return None

        np.random.seed(42)
        n = 1000

        cpu      = np.random.uniform(5, 95, n)
        memory   = np.random.uniform(50, 99, n)
        disk     = np.random.uniform(20, 80, n)
        network  = np.random.uniform(0, 100, n)
        procs    = np.random.randint(100, 400, n)

        labels = []
        for i in range(n):
            risk = 0
            if cpu[i]     > 85: risk += 2
            if memory[i]  > 85: risk += 2
            if disk[i]    > 90: risk += 2
            if network[i] > 70: risk += 1
            if procs[i]   > 300: risk += 1
            if cpu[i] > 75 and memory[i] > 80:
                risk += 2
            labels.append(1 if risk >= 3 else 0)

        df = pd.DataFrame({
            "CPU"       : cpu,
            "Memory"    : memory,
            "Disk"      : disk,
            "Network"   : network,
            "Processes" : procs,
            "Failure"   : labels
        })

        os.makedirs(
            "system_prediction/dataset",
            exist_ok=True
        )
        df.to_csv(
            "system_prediction/dataset/"
            "system_metrics.csv",
            index=False
        )

        X = df[["CPU", "Memory", "Disk",
                "Network", "Processes"]]
        y = df["Failure"]

        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        model.fit(X, y)

        os.makedirs(
            "system_prediction/models",
            exist_ok=True
        )
        save_path = os.path.join(
            "system_prediction",
            "models",
            "failure_model.pkl"
        )
        joblib.dump(model, save_path)
        self.use_full_features = True
        log_success("New model trained and saved!")
        return model

    def predict(self, metrics):
        if self.model is None:
            return "NORMAL"

        # ---------------------------------------------------------
        # Manual / config threshold override (for on-demand testing)
        #
        # Lets you force a FAILURE result without waiting on the ML
        # model, by editing CPU_THRESHOLD / MEMORY_THRESHOLD /
        # DISK_THRESHOLD in config.py. Keep these at realistic values
        # (85 / 85 / 90) for normal operation - lower them temporarily
        # only when you want to trigger a test failure on demand.
        # ---------------------------------------------------------
        cpu    = metrics.get("cpu", metrics.get("CPU", 0))
        memory = metrics.get("memory", metrics.get("Memory", 0))
        disk   = metrics.get("disk", metrics.get("Disk", 0))

        try:
            from config import (
                CPU_THRESHOLD,
                MEMORY_THRESHOLD,
                DISK_THRESHOLD
            )
            if (cpu > CPU_THRESHOLD or
                memory > MEMORY_THRESHOLD or
                disk > DISK_THRESHOLD):
                self.last_probability = 95.0
                print(
                    f"⚠ WARNING: THRESHOLD BREACH! "
                    f"CPU:{cpu}% MEM:{memory}% DISK:{disk}%"
                )
                return "FAILURE"
        except Exception:
            pass
        # ----------------------- end override -----------------------

        try:
            if self.use_full_features:
                live_data = pd.DataFrame([{
                    "CPU"       : metrics.get(
                        "cpu",
                        metrics.get("CPU", 0)
                    ),
                    "Memory"    : metrics.get(
                        "memory",
                        metrics.get("Memory", 0)
                    ),
                    "Disk"      : metrics.get(
                        "disk",
                        metrics.get("Disk", 0)
                    ),
                    "Network"   : metrics.get(
                        "network",
                        metrics.get("Network", 0)
                    ),
                    "Processes" : metrics.get(
                        "processes",
                        metrics.get(
                            "process_count",
                            metrics.get(
                                "Processes", 0
                            )
                        )
                    )
                }])
            else:
                live_data = pd.DataFrame([{
                    "CPU"    : metrics.get(
                        "cpu",
                        metrics.get("CPU", 0)
                    ),
                    "Memory" : metrics.get(
                        "memory",
                        metrics.get("Memory", 0)
                    ),
                    "Disk"   : metrics.get(
                        "disk",
                        metrics.get("Disk", 0)
                    )
                }])

            prediction  = self.model.predict(
                live_data
            )[0]
            probability = self.model.predict_proba(
                live_data
            )[0][1]

            self.last_probability = round(
                probability * 100, 2
            )

            health_score = round(
                (1 - probability) * 100, 2
            )

            if prediction == 1:
                if probability >= 0.80:
                    severity = "Critical"
                elif probability >= 0.60:
                    severity = "High"
                else:
                    severity = "Medium"

                print(
                    f"⚠ WARNING: FAILURE LIKELY! "
                    f"Probability: "
                    f"{self.last_probability}% "
                    f"Severity: {severity}"
                )
                return "FAILURE"

            else:
                print(
                    f"✅ System Healthy | "
                    f"Failure Prob: "
                    f"{self.last_probability}% | "
                    f"Health Score: {health_score}%"
                )
                return "NORMAL"

        except Exception as e:
            log_warning(f"Prediction error: {e}")
            return "NORMAL"