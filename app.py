# app.py - COMPLETE MERGED VERSION WITH ALERTS (FIXED)

try:
    from flask import (
        Flask, render_template,
        request, redirect,
        session, jsonify
    )
except ImportError:  # pragma: no cover
    Flask = render_template = request = redirect = session = jsonify = None
import os
IS_VERCEL = os.getenv("VERCEL") == "1"
import threading
import time
import sys

# Add paths
sys.path.insert(0, 'modules/')
sys.path.insert(0, 'backup/')
sys.path.insert(0, 'cloud/')

# Your existing imports
from dashboard.dashboard_data    import get_dashboard_data
from quarantine.metadata_manager import MetadataManager
from quarantine.authentication   import authenticate
from quarantine.delete_manager   import delete_file
from quarantine.restore_manager  import restore_file
from monitor.file_monitor        import start_monitor

# New backup imports
from modules.system_monitor     import SystemMonitor
from modules.failure_prediction import FailurePrediction
from modules.anomaly_detection  import AnomalyDetection
from modules.malware_detection  import MalwareDetection
from backup.backup_manager      import BackupManager
from backup.recovery_engine     import RecoveryEngine
from alerts.alert_manager       import AlertManager
from logger import log_info, log_warning, log_success

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set"
    )
# NOTE: move SECRET_KEY (and any API tokens) into environment variables /
# a .env file before deploying. Never hardcode real secrets in source.

# Global system status
system_status = {
    "cpu"                : 0,
    "memory"             : 0,
    "disk"               : 0,
    "network_sent"       : 0,
    "network_recv"       : 0,
    "network_speed_up"   : 0,
    "network_speed_down" : 0,
    "process_count"      : 0,
    "top_processes"      : [],
    "status"             : "Normal",
    "last_backup"        : "Never",
    "backup_clouds"      : [],
    "last_recovery"      : "Never",
    "rto"                : "N/A",
    "threats"            : 0,
    "failure_probability": 0,
    "monitor_ready"      : False  # NEW: tells us if the background thread actually initialized
}

# Initialize backup modules
backup_mgr   = None
recovery_eng = None

# ================================
# Background System Monitor Thread
# ================================

def system_monitor_thread():
    global system_status
    global backup_mgr
    global recovery_eng

    system_status["monitor_ready"] = False

    # ============================
    # Module initialization
    # ============================
    # Wrapped in try/except so a bad credential file, missing model, etc.
    # doesn't silently kill this thread with no trace. If this fails, CPU/
    # memory stats, backups, and recovery will all stay frozen/unavailable
    # until it's fixed - the log line below is the signal to check.
    try:
        monitor      = SystemMonitor()
        failure_pred = FailurePrediction()
        anomaly_det  = AnomalyDetection()
        malware_det  = MalwareDetection()
        backup_mgr   = BackupManager()
        recovery_eng = RecoveryEngine(
            backup_mgr.gdrive,
            backup_mgr.onedrive,
            backup_mgr.dropbox
        )
    except Exception as e:
        log_warning(f"FATAL: monitor thread failed to initialize: {e}")
        system_status["status"] = "Monitor Init Failed"
        return

    log_success("All modules initialized!")
    system_status["monitor_ready"] = True

    # Initial backup
    try:
        backup_mgr.create_backup(reason="System Startup")
        system_status["last_backup"] = time.strftime("%H:%M:%S")
    except Exception as e:
        log_warning(f"Startup backup failed: {e}")

    try:
        import schedule
    except ImportError:  # pragma: no cover
        schedule = None
        next_hourly_backup = time.time() + 3600
        log_warning(
            "schedule is not installed; using the internal hourly "
            "backup timer."
        )
    else:
        schedule.every(1).hour.do(
            backup_mgr.create_backup,
            reason="Scheduled Hourly"
        )

    while True:
        try:
            # ============================
            # STEP 1 - Collect Metrics
            # ============================
            metrics = monitor.collect_metrics()

            # Update global status
            system_status["cpu"]    = metrics["cpu"]
            system_status["memory"] = metrics["memory"]
            system_status["disk"]   = metrics["disk"]
            system_status["network_sent"]       = \
                metrics.get("network_sent", 0)
            system_status["network_recv"]       = \
                metrics.get("network_recv", 0)
            system_status["network_speed_up"]   = \
                metrics.get("network_speed_up", 0)
            system_status["network_speed_down"] = \
                metrics.get("network_speed_down", 0)
            system_status["process_count"]      = \
                metrics.get("process_count", 0)
            system_status["top_processes"]      = \
                metrics.get("top_processes", [])

            # ============================
            # STEP 2 - Failure Prediction
            # ============================
            failure     = failure_pred.predict(metrics)
            probability = getattr(
                failure_pred,
                'last_probability',
                0
            )
            system_status["failure_probability"] = \
                probability

            if failure == "FAILURE":
                system_status["status"] = \
                    "FAILURE DETECTED"
                log_warning("Failure detected!")

                # Determine severity
                if probability >= 80:
                    severity = "Critical"
                elif probability >= 60:
                    severity = "High"
                else:
                    severity = "Medium"

                # Create failure alert
                AlertManager.add_failure_alert(
                    metrics     = metrics,
                    probability = probability,
                    severity    = severity
                )

                # Create backup
                backup_mgr.create_backup(
                    reason="Failure Detected"
                )
                system_status["last_backup"] = \
                    time.strftime("%H:%M:%S")

                # Recovery
                result = recovery_eng.restore(
                    reason="System Failure"
                )

                if result:
                    system_status["last_recovery"] = \
                        time.strftime("%H:%M:%S")
                    system_status["status"] = "Recovered"

                    # Auto resolve alert
                    all_alerts = AlertManager.get_all()
                    active = [
                        a for a in all_alerts
                        if a["status"] == "Active"
                        and a["type"] == "failure"
                    ]
                    if active:
                        AlertManager.resolve_alert(
                            active[0]["id"]
                        )
                else:
                    log_warning(
                        "Auto-recovery failed: no backup "
                        "source succeeded."
                    )

            else:
                system_status["status"] = "Normal"

            # ============================
            # STEP 3 - Anomaly Detection
            # ============================
            anomaly = anomaly_det.detect(metrics)

            if anomaly == "ANOMALY":
                log_warning("Anomaly detected!")
                malware_det.scan_directory(
                    "critical_data/"
                )

            # ============================
            # STEP 4 - Malware Check
            # ============================
            if malware_det.malware_found:
                system_status["threats"] += 1
                system_status["status"] = \
                    "MALWARE DETECTED"

                infected = malware_det.infected_file

                # Create malware alert
                AlertManager.add_malware_alert(
                    filename     = infected,
                    threat_level = "Critical",
                    malware_type = "Malicious Executable",
                    action_taken = (
                        "Quarantined + "
                        "Backup Created + "
                        "System Recovered"
                    )
                )

                # Quarantine file
                if infected:
                    _quarantine_file(infected)

                # Backup
                backup_mgr.create_backup(
                    reason="Malware Detected"
                )
                system_status["last_backup"] = \
                    time.strftime("%H:%M:%S")

                # Recovery
                malware_result = recovery_eng.restore(
                    reason="Malware Detected"
                )
                if malware_result:
                    system_status["last_recovery"] = \
                        time.strftime("%H:%M:%S")
                else:
                    log_warning(
                        "Post-malware recovery failed: no "
                        "backup source succeeded."
                    )

                malware_det.malware_found = False
                malware_det.infected_file = None

            if schedule is not None:
                schedule.run_pending()
            elif time.time() >= next_hourly_backup:
                try:
                    backup_mgr.create_backup(reason="Scheduled Hourly")
                    system_status["last_backup"] = time.strftime("%H:%M:%S")
                except Exception as e:
                    log_warning(f"Scheduled backup failed: {e}")
                finally:
                    next_hourly_backup = time.time() + 3600

            time.sleep(5)

        except Exception as e:
            log_warning(f"Monitor error: {e}")
            time.sleep(5)


def _quarantine_file(filepath):
    import shutil
    quarantine = "storage/quarantine/"
    os.makedirs(quarantine, exist_ok=True)
    try:
        dest = os.path.join(
            quarantine,
            os.path.basename(filepath)
        )
        shutil.move(filepath, dest)
        log_success(
            f"Quarantined: {os.path.basename(filepath)}"
        )
    except Exception as e:
        log_warning(f"Quarantine error: {e}")


# ================================
# EXISTING ROUTES
# ================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if authenticate(username, password):
            session["logged_in"] = True
            return redirect("/")

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template("login.html", error=None)


@app.route("/")
def dashboard():
    if not session.get("logged_in"):
        return redirect("/login")

    data          = get_dashboard_data()
    alert_stats   = AlertManager.get_stats()
    recent_alerts = AlertManager.get_all()[:5]  # already newest-first

    data["system_status"]  = system_status
    data["active_alerts"]  = alert_stats["active"]
    data["alert_stats"]    = alert_stats
    data["recent_alerts"]  = recent_alerts

    return render_template(
        "dashboard.html",
        stats         = data,
        files         = data["files"],
        active_alerts = alert_stats["active"]
    )


@app.route("/repository")
def repository():
    if not session.get("logged_in"):
        return redirect("/login")

    files = MetadataManager.all()

    return render_template(
        "repository.html",
        files=files[::-1]
    )


@app.route("/analytics")
def analytics():
    if not session.get("logged_in"):
        return redirect("/login")

    return render_template("analytics.html")


@app.route("/logs")
def logs():
    if not session.get("logged_in"):
        return redirect("/login")

    return render_template("logs.html")


@app.route("/settings")
def settings():
    if not session.get("logged_in"):
        return redirect("/login")

    return render_template("settings.html")


@app.route("/restore/<int:file_id>")
def restore(file_id):
    if not session.get("logged_in"):
        return redirect("/login")

    restore_file(file_id)
    return redirect("/repository")


@app.route("/delete/<int:file_id>")
def delete(file_id):
    if not session.get("logged_in"):
        return redirect("/login")

    delete_file(file_id)
    return redirect("/repository")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ================================
# BACKUP ROUTES
# ================================

@app.route("/backup")
def backup_page():
    if not session.get("logged_in"):
        return redirect("/login")

    return render_template(
        "backup.html",
        status=system_status
    )


@app.route("/manual_backup")
def manual_backup():
    if not session.get("logged_in"):
        return redirect("/login")

    if backup_mgr:
        backup_mgr.create_backup(
            reason="Manual Backup"
        )
        system_status["last_backup"] = \
            time.strftime("%H:%M:%S")
    else:
        log_warning(
            "Manual backup requested, but backup manager "
            "isn't ready yet (check startup logs)."
        )

    return redirect("/backup")


@app.route("/manual_recovery")
def manual_recovery():
    if not session.get("logged_in"):
        return redirect("/login")

    if recovery_eng:
        success = recovery_eng.restore(
            reason="Manual Recovery"
        )
        if success:
            system_status["last_recovery"] = \
                time.strftime("%H:%M:%S")
            system_status["status"] = "Recovered"
        else:
            log_warning(
                "Manual recovery ran but all backup "
                "sources failed."
            )
    else:
        log_warning(
            "Manual recovery requested, but recovery "
            "engine isn't ready yet (check startup logs)."
        )

    return redirect("/backup")


@app.route("/system_status")
def get_system_status():
    return jsonify(system_status)

@app.route("/live_data")
def live_data():
    data = get_dashboard_data()

    alert_stats = AlertManager.get_stats()

    return jsonify({
        "scanned": data["scanned"],
        "safe": data["safe"],
        "quarantined": data["quarantined"],
        "critical": data["critical"],
        "high": data["high"],
        "medium": data["medium"],
        "restored": data["restored"],
        "files": data["files"],
        "watch_folders": data["watch_folders"],
        "system_status": system_status,
        "alerts": AlertManager.get_all()[:10],
        "alert_stats": alert_stats
    })

# ================================
# ALERT ROUTES
# ================================

@app.route("/alerts")
def alerts_page():
    if not session.get("logged_in"):
        return redirect("/login")

    all_alerts = AlertManager.get_all()
    stats      = AlertManager.get_stats()

    failure_alerts = [
        a for a in all_alerts
        if a["type"] == "failure"
    ]
    malware_alerts = [
        a for a in all_alerts
        if a["type"] == "malware"
    ]

    return render_template(
        "alerts.html",
        failure_alerts = failure_alerts,
        malware_alerts = malware_alerts,
        stats          = stats
    )


@app.route("/resolve/<int:alert_id>")
def resolve_alert(alert_id):
    if not session.get("logged_in"):
        return redirect("/login")

    AlertManager.resolve_alert(alert_id)
    return redirect("/alerts")


@app.route("/alerts_data")
def alerts_data():
    return jsonify({
        "alerts" : AlertManager.get_all(),
        "stats"  : AlertManager.get_stats()
    })


# ================================
# MAIN
# ================================

if __name__ == "__main__":

    # ==========================================
    # LOCAL MODE
    # ==========================================
    if not IS_VERCEL:

        from monitor.file_monitor import start_monitor

        # --------------------------------------
        # Start System Monitor
        # --------------------------------------
        system_thread = threading.Thread(
            target=system_monitor_thread,
            daemon=True
        )

        system_thread.start()

        log_success(
            "System monitoring thread started."
        )

        # --------------------------------------
        # Start File Monitor in background
        # --------------------------------------
        file_thread = threading.Thread(
            target=start_monitor,
            daemon=True
        )

        file_thread.start()

        log_success(
            "File monitoring thread started."
        )

    # ==========================================
    # START FLASK
    # ==========================================

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
