import os
import datetime
import ctypes
import logging
from core.utils import is_admin

class SafetyManager:
    def __init__(self):
        self.setup_logging()

    def setup_logging(self):
        log_dir = "logs"
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"cleaner_{datetime.date.today()}.log")
            logging.basicConfig(
                filename=log_file,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        except Exception:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        self.logger = logging.getLogger('SafetyLogger')

    def log_action(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)

    def create_restore_point(self, description="Cleaner Wannabe Restore Point"):
        if not is_admin():
            self.log_error("Cannot create restore point: Not Admin")
            return False, "Not Admin"

        try:
            # Uses standard Windows API via ctypes or powershell
            # PowerShell is easier and more reliable for this specific task in Python without complex wmi wrappers
            cmd = f'Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"'
            # We run this via powershell
            # Note: This requires the feature to be enabled on Windows.
            import subprocess
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log_action(f"Restore Point created: {description}")
                return True, "Restore Point Created"
            else:
                err = (result.stderr or result.stdout).strip()
                self.log_error(f"Failed to create restore point: {err}")
                return False, f"Failed: {err}"
        except Exception as e:
            self.log_error(f"Error creating restore point: {e}")
            return False, str(e)
