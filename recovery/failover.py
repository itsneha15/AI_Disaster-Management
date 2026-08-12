# recovery/failover.py

from logger import log_warning

def disaster_recovery(prediction):
    if prediction == 1:
        print("\n🔄 DISASTER RECOVERY TRIGGERED!")
        log_warning("Failover initiated!")
        return True
    return False