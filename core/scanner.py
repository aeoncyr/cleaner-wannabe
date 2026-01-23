import os
import shutil
import winshell
from .utils import is_admin, get_system_drive

class Scanner:
    def __init__(self):
        self.scan_results = {}  # category -> {files: [], size: 0}
        self.categories = {
            'System Temp': self.scan_temp,
            'Recycle Bin': self.scan_recycle_bin,
            'Prefetch': self.scan_prefetch,
            'Chrome Cache': lambda: self.scan_browser('Chrome'),
            'Edge Cache': lambda: self.scan_browser('Edge'),
            'Windows Logs': self.scan_logs,
            'Crash Dumps': self.scan_crash_dumps,
        }

    def scan_logs(self):
        # C:\Windows\Logs
        if not is_admin():
             return {'files': [], 'size': 0}

        log_path = os.path.join(os.environ.get('SystemRoot'), 'Logs')
        return self._generic_scan(log_path, ['.log'])

    def scan_crash_dumps(self):
        # C:\Windows\Minidump and %LOCALAPPDATA%\CrashDumps
        files = []
        total_size = 0
        
        # System Dumps
        if is_admin():
            sys_dump = os.path.join(os.environ.get('SystemRoot'), 'Minidump')
            res = self._generic_scan(sys_dump)
            files.extend(res['files'])
            total_size += res['size']
            
        # User Dumps
        local_app_data = os.environ.get('LOCALAPPDATA')
        if local_app_data:
            user_dump = os.path.join(local_app_data, 'CrashDumps')
            res = self._generic_scan(user_dump)
            files.extend(res['files'])
            total_size += res['size']
            
        return {'files': files, 'size': total_size}

    def _generic_scan(self, path, extensions=None):
        if not path or not os.path.exists(path):
             return {'files': [], 'size': 0}
        
        files_found = []
        total_size = 0
        for root, dirs, files in os.walk(path):
            for name in files:
                if extensions and not any(name.lower().endswith(ext) for ext in extensions):
                    continue
                try:
                    filepath = os.path.join(root, name)
                    size = os.path.getsize(filepath)
                    files_found.append(filepath)
                    total_size += size
                except:
                    pass
        return {'files': files_found, 'size': total_size}

    def scan_temp(self):
        temp_paths = [os.environ.get('TEMP')]
        if is_admin():
            temp_paths.append(os.path.join(os.environ.get('SystemRoot'), 'Temp'))

        files_found = []
        total_size = 0

        for path in temp_paths:
             res = self._generic_scan(path)
             files_found.extend(res['files'])
             total_size += res['size']
        
        return {'files': files_found, 'size': total_size}

    def scan_browser(self, browser_name):
         local_app_data = os.environ.get('LOCALAPPDATA')
         if not local_app_data:
            return {'files': [], 'size': 0}
            
         paths = {
            'Chrome': os.path.join(local_app_data, r'Google\Chrome\User Data\Default\Cache\Cache_Data'),
            'Edge': os.path.join(local_app_data, r'Microsoft\Edge\User Data\Default\Cache\Cache_Data'),
         }
         
         target_path = paths.get(browser_name)
         if target_path:
             return self._generic_scan(target_path)
         return {'files': [], 'size': 0}


    def scan_recycle_bin(self):
        # Using winshell to get recycle bin content is tricky to list individually without emptying
        # For v1 we will rely on a generic size estimate or skipping individual file listing if complex.
        # Actually, let's try to iterate nicely if possible, or just use a known trick.
        # Simple approach: Return a placeholder that says "Recycle Bin" and we use a different method to clean.
        # BUT, standard python 'winshell' allows iterating.
        
        files_found = []
        total_size = 0
        
        try:
            # winshell.recycle_bin() returns an iterator of deleted items
            for item in winshell.recycle_bin():
                 # item.original_filename(), item.size()
                 files_found.append(f"[Recycle Bin] {item.original_filename()}")
                 total_size += item.size()
        except:
             # Fallback or permission issues
             pass

        return {'files': files_found, 'size': total_size}
        
    def scan_prefetch(self):
        if not is_admin():
            return {'files': [], 'size': 0}
            
        prefetch_path = os.path.join(os.environ.get('SystemRoot'), 'Prefetch')
        files_found = []
        total_size = 0
        
        if os.path.exists(prefetch_path):
             for root, dirs, files in os.walk(prefetch_path):
                for name in files:
                    if name.lower().endswith('.pf'):
                        try:
                            filepath = os.path.join(root, name)
                            size = os.path.getsize(filepath)
                            files_found.append(filepath)
                            total_size += size
                        except:
                            pass

        return {'files': files_found, 'size': total_size}





    def scan_selected(self, selected_categories):
        # Reset results for selected only or all?
        # Let's clean scan_results for selected
        for cat in selected_categories:
            if cat in self.categories:
                self.scan_results[cat] = self.categories[cat]()
        return self.scan_results

    def scan_all(self):
        return self.scan_selected(self.categories.keys())
