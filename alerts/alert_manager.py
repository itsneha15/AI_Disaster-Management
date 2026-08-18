# alerts/alert_manager.py

import json
import os
from datetime import datetime

if os.getenv("VERCEL"):
    ALERTS_FILE = "/tmp/ai_disaster_alerts.json"
else:
    ALERTS_FILE = "storage/alerts.json"

class AlertManager:

    @staticmethod
    def init():

        parent = os.path.dirname(ALERTS_FILE)

        if parent:
            os.makedirs(parent, exist_ok=True)

        if not os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, "w") as f:
                json.dump([], f)

    @staticmethod
    def add_failure_alert(
        metrics,
        probability,
        severity
    ):
        AlertManager.init()

        try:
            with open(ALERTS_FILE, 'r') as f:
                alerts = json.load(f)
        except:
            alerts = []

        if probability >= 80:
            action = (
                "CRITICAL: Immediate backup "
                "and recovery required!"
            )
        elif probability >= 60:
            action = (
                "HIGH: Create backup "
                "immediately"
            )
        else:
            action = (
                "MEDIUM: Monitor system "
                "closely"
            )

        alert = {
            "id"          : len(alerts) + 1,
            "type"        : "failure",
            "timestamp"   : datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "severity"    : severity,
            "probability" : f"{probability}%",
            "metrics"     : {
                "cpu"      : metrics.get(
                    "cpu",
                    metrics.get("CPU", 0)
                ),
                "memory"   : metrics.get(
                    "memory",
                    metrics.get("Memory", 0)
                ),
                "disk"     : metrics.get(
                    "disk",
                    metrics.get("Disk", 0)
                ),
                "network"  : metrics.get(
                    "network",
                    metrics.get("Network", 0)
                ),
                "processes": metrics.get(
                    "processes",
                    metrics.get(
                        "process_count",
                        metrics.get("Processes", 0)
                    )
                )
            },
            "recommended_action" : action,
            "status"             : "Active"
        }

        alerts.append(alert)

        with open(ALERTS_FILE, 'w') as f:
            json.dump(alerts, f, indent=4)

        return alert

    @staticmethod
    def add_malware_alert(
        filename,
        threat_level,
        malware_type,
        action_taken
    ):
        AlertManager.init()

        try:
            with open(ALERTS_FILE, 'r') as f:
                alerts = json.load(f)
        except:
            alerts = []

        alert = {
            "id"           : len(alerts) + 1,
            "type"         : "malware",
            "timestamp"    : datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "filename"     : os.path.basename(
                str(filename)
            ) if filename else "Unknown",
            "threat_level" : threat_level,
            "malware_type" : malware_type,
            "action_taken" : action_taken,
            "status"       : "Active"
        }

        alerts.append(alert)

        with open(ALERTS_FILE, 'w') as f:
            json.dump(alerts, f, indent=4)

        return alert

    @staticmethod
    def resolve_alert(alert_id):
        AlertManager.init()
        try:
            with open(ALERTS_FILE, 'r') as f:
                alerts = json.load(f)

            for alert in alerts:
                if alert["id"] == int(alert_id):
                    alert["status"] = "Resolved"
                    break

            with open(ALERTS_FILE, 'w') as f:
                json.dump(alerts, f, indent=4)
            return True
        except:
            return False

    @staticmethod
    def get_all():
        AlertManager.init()
        try:
            with open(ALERTS_FILE, 'r') as f:
                return json.load(f)[::-1]
        except:
            return []

    @staticmethod
    def get_stats():
        alerts = AlertManager.get_all()
        return {
            "total"    : len(alerts),
            "active"   : len([
                a for a in alerts
                if a["status"] == "Active"
            ]),
            "resolved" : len([
                a for a in alerts
                if a["status"] == "Resolved"
            ]),
            "failure"  : len([
                a for a in alerts
                if a["type"] == "failure"
            ]),
            "malware"  : len([
                a for a in alerts
                if a["type"] == "malware"
            ])
        }