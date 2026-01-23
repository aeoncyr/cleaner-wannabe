import os
import winshell
import shutil
import send2trash
from core.safety import SafetyManager

class Cleaner:
    def __init__(self):
        self.safety = SafetyManager()

    def clean_files(self, files_list, use_recycle_bin=False):
        cleaned_count = 0
        cleaned_size = 0
        errors = []

        for filepath in files_list:
            # Special handling for Recycle Bin
            if filepath.startswith("[Recycle Bin]"):
                continue # Handled separately

            try:
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    if use_recycle_bin:
                         send2trash.send2trash(filepath)
                         self.safety.log_action(f"Moved to Recycle Bin: {filepath}")
                    else:
                        os.remove(filepath)
                        self.safety.log_action(f"Deleted: {filepath} ({size} bytes)")
                    
                    cleaned_count += 1
                    cleaned_size += size
                elif os.path.isdir(filepath):
                    # We usually don't delete dirs in this simple list unless specified, 
                    # but scanner currently returns files. 
                    pass
            except Exception as e:
                err_msg = f"Failed to delete {filepath}: {e}"
                errors.append(err_msg)
                self.safety.log_error(err_msg)

        return cleaned_count, cleaned_size, errors

    def clean_recycle_bin(self):
        try:
            # This empties the recycle bin for real
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            self.safety.log_action("Emptied Recycle Bin")
            return True, "Recycle Bin Empty"
        except Exception as e:
            self.safety.log_error(f"Failed to empty Recycle Bin: {e}")
            return False, str(e)

    def clean_category(self, category_name, scan_result_for_category, use_recycle_bin=False):
        self.safety.log_action(f"Starting clean for category: {category_name}")
        
        files = scan_result_for_category.get('files', [])
        total_size = scan_result_for_category.get('size', 0)

        if category_name == 'Recycle Bin':
            # Recycle bin cannot be sent to recycle bin. It must be emptied.
            success, msg = self.clean_recycle_bin()
            if success:
                # Assuming all found items were deleted
                return len(files), total_size, []
            else:
                return 0, 0, [msg]
        
        return self.clean_files(files, use_recycle_bin)

    def run_safety_checks(self):
        # Create Restore Point (only tries if Admin)
        success, msg = self.safety.create_restore_point()
        return success, msg
