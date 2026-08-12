from alerts.alert_manager import AlertManager

AlertManager.add_failure_alert(
    metrics={
        "cpu": 92,
        "memory": 88,
        "disk": 75,
        "network": 65,
        "processes": 320
    },
    probability=85.5,
    severity="Critical"
)

AlertManager.add_malware_alert(
    filename="test_virus.exe",
    threat_level="Critical",
    malware_type="Trojan",
    action_taken="Quarantined"
)

print("Test alerts created successfully!")