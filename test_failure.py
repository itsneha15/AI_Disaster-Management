# test_failure.py
# Run this separately to test everything

import sys
import os
import time

sys.path.insert(0, 'modules/')
sys.path.insert(0, 'backup/')
sys.path.insert(0, 'cloud/')

from backup.backup_manager  import BackupManager
from backup.recovery_engine import RecoveryEngine
from alerts.alert_manager   import AlertManager
from logger import log_info, log_success

def test_complete_system():
    print("\n" + "="*50)
    print("  SYSTEM FAILURE TEST")
    print("="*50)

    # Fake failure metrics
    test_metrics = {
        "cpu"            : 98,
        "memory"         : 97,
        "disk"           : 95,
        "network"        : 90,
        "processes"      : 400,
        "upload_speed"   : 50,
        "download_speed" : 60,
        "CPU"            : 98,
        "Memory"         : 97,
        "Disk"           : 95,
        "Network"        : 90,
        "Processes"      : 400
    }

    print("\n📊 Simulated System Metrics:")
    print(f"CPU      : {test_metrics['cpu']}%")
    print(f"Memory   : {test_metrics['memory']}%")
    print(f"Disk     : {test_metrics['disk']}%")
    print(f"Network  : {test_metrics['network']}%")
    print(f"Processes: {test_metrics['processes']}")

    # Step 1 - Generate Alert
    print("\n" + "-"*40)
    print("STEP 1: Generating Alert...")
    print("-"*40)

    alert = AlertManager.add_failure_alert(
        metrics     = test_metrics,
        probability = 95.5,
        severity    = "Critical"
    )

    print(f"✅ Alert Created!")
    print(f"   Alert ID  : #{alert['id']}")
    print(f"   Severity  : {alert['severity']}")
    print(f"   Probability: {alert['probability']}")
    print(f"   Action    : {alert['recommended_action']}")
    print(f"   Status    : {alert['status']}")

    # Step 2 - Create Backup
    print("\n" + "-"*40)
    print("STEP 2: Creating Backup...")
    print("-"*40)

    backup_mgr = BackupManager()

    result = backup_mgr.create_backup(
        reason="Test Failure Detected"
    )

    if result:
        print("✅ Backup created successfully!")
    else:
        print("❌ Backup failed!")

    # Step 3 - Test Recovery
    print("\n" + "-"*40)
    print("STEP 3: Testing Recovery...")
    print("-"*40)

    recovery_eng = RecoveryEngine(
        backup_mgr.gdrive,
        backup_mgr.onedrive,
        backup_mgr.dropbox
    )

    result = recovery_eng.restore(
        reason="Test Recovery"
    )

    if result:
        print("✅ Recovery successful!")
    else:
        print("❌ Recovery failed!")

    # Step 4 - Show Alert Summary
    print("\n" + "-"*40)
    print("STEP 4: Alert Summary")
    print("-"*40)

    stats = AlertManager.get_stats()
    print(f"Total Alerts   : {stats['total']}")
    print(f"Active Alerts  : {stats['active']}")
    print(f"Failure Alerts : {stats['failure']}")
    print(f"Malware Alerts : {stats['malware']}")

    print("\n" + "="*50)
    print("  TEST COMPLETE!")
    print("  Check alerts at:")
    print("  http://127.0.0.1:5000/alerts")
    print("="*50)

    # Add after Step 4 in test_failure.py

# Step 5 - Test Malware Alert
print("\n" + "-"*40)
print("STEP 5: Testing Malware Alert...")
print("-"*40)

malware_alert = AlertManager.add_malware_alert(
    filename     = "test_virus.exe",
    threat_level = "Critical",
    malware_type = "Trojan",
    action_taken = "Quarantined + Backup + Recovery"
)

print(f"✅ Malware Alert Created!")
print(f"   Alert ID    : #{malware_alert['id']}")
print(f"   File        : {malware_alert['filename']}")
print(f"   Threat      : {malware_alert['threat_level']}")
print(f"   Type        : {malware_alert['malware_type']}")
print(f"   Action      : {malware_alert['action_taken']}")
print(f"   Status      : {malware_alert['status']}")

if __name__ == "__main__":
    test_complete_system()