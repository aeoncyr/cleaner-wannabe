import os
import time
import winshell
from .utils import is_admin

class Scanner:
    def __init__(self):
        self.scan_results = {}  # category -> {files: [], size: 0}
        self.categories = {
            'System Temp': self.scan_temp,
            'Recycle Bin': self.scan_recycle_bin,
            'Prefetch': self.scan_prefetch,
            'Chrome Cache': self.scan_chrome_cache,
            'Edge Cache': self.scan_edge_cache,
            'Windows Logs': self.scan_logs,
            'Crash Dumps': self.scan_crash_dumps,
            'Windows Update Cache': self.scan_windows_update_cache,
            'Thumbnail Cache': self.scan_thumbnail_cache,
            'DirectX Shader Cache': self.scan_shader_cache,
            'Windows Error Reports': self.scan_error_reports,
        }

    def _is_old_enough(self, filepath, min_age_days):
        if not min_age_days or min_age_days <= 0:
            return True
        try:
            mtime = os.path.getmtime(filepath)
        except Exception:
            return False
        age_seconds = time.time() - mtime
        return age_seconds >= (min_age_days * 86400)

    def _merge_results(self, results):
        files = []
        items = []
        total_size = 0
        skipped_recent = 0
        skipped_recent_size = 0
        for res in results:
            files.extend(res.get('files', []))
            items.extend(res.get('items', []))
            total_size += res.get('size', 0)
            skipped_recent += res.get('skipped_recent', 0)
            skipped_recent_size += res.get('skipped_recent_size', 0)
        return {
            'files': files,
            'items': items,
            'size': total_size,
            'skipped_recent': skipped_recent,
            'skipped_recent_size': skipped_recent_size,
        }

    def scan_logs(self, min_age_days=None):
        # C:\Windows\Logs
        if not is_admin():
             return {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

        system_root = os.environ.get('SystemRoot')
        if not system_root:
            return {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

        log_path = os.path.join(system_root, 'Logs')
        return self._generic_scan(log_path, ['.log'], min_age_days=min_age_days)

    def scan_crash_dumps(self, min_age_days=None):
        # C:\Windows\Minidump and %LOCALAPPDATA%\CrashDumps
        results = []
        
        # System Dumps
        if is_admin():
            sys_dump = os.path.join(os.environ.get('SystemRoot'), 'Minidump')
            results.append(self._generic_scan(sys_dump, min_age_days=min_age_days))
            
        # User Dumps
        local_app_data = os.environ.get('LOCALAPPDATA')
        if local_app_data:
            user_dump = os.path.join(local_app_data, 'CrashDumps')
            results.append(self._generic_scan(user_dump, min_age_days=min_age_days))
            
        return self._merge_results(results) if results else {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

    def _generic_scan(self, path, extensions=None, name_predicate=None, min_age_days=None):
        if not path or not os.path.exists(path):
             return {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}
        
        files_found = []
        items = []
        total_size = 0
        skipped_recent = 0
        skipped_recent_size = 0
        for root, dirs, files in os.walk(path):
            for name in files:
                if extensions and not any(name.lower().endswith(ext) for ext in extensions):
                    continue
                if name_predicate and not name_predicate(name):
                    continue
                try:
                    filepath = os.path.join(root, name)
                    if not self._is_old_enough(filepath, min_age_days):
                        skipped_recent += 1
                        try:
                            skipped_recent_size += os.path.getsize(filepath)
                        except Exception:
                            pass
                        continue
                    size = os.path.getsize(filepath)
                    files_found.append(filepath)
                    items.append({'path': filepath, 'size': size})
                    total_size += size
                except Exception:
                    pass
        return {
            'files': files_found,
            'items': items,
            'size': total_size,
            'skipped_recent': skipped_recent,
            'skipped_recent_size': skipped_recent_size,
        }

    def scan_temp(self, min_age_days=None):
        temp_paths = [os.environ.get('TEMP')]
        if is_admin():
            temp_paths.append(os.path.join(os.environ.get('SystemRoot'), 'Temp'))

        results = []

        for path in temp_paths:
             results.append(self._generic_scan(path, min_age_days=min_age_days))
        
        return self._merge_results(results) if results else {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

    def scan_browser(self, browser_name, min_age_days=None):
         local_app_data = os.environ.get('LOCALAPPDATA')
         if not local_app_data:
            return {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}
            
         paths = {
            'Chrome': os.path.join(local_app_data, r'Google\Chrome\User Data\Default\Cache\Cache_Data'),
            'Edge': os.path.join(local_app_data, r'Microsoft\Edge\User Data\Default\Cache\Cache_Data'),
         }
         
         target_path = paths.get(browser_name)
         if target_path:
             return self._generic_scan(target_path, min_age_days=min_age_days)
         return {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

    def scan_chrome_cache(self, min_age_days=None):
        return self.scan_browser('Chrome', min_age_days=min_age_days)

    def scan_edge_cache(self, min_age_days=None):
        return self.scan_browser('Edge', min_age_days=min_age_days)

    def scan_recycle_bin(self, min_age_days=None):
        # Using winshell to get recycle bin content is tricky to list individually without emptying
        # For v1 we will rely on a generic size estimate or skipping individual file listing if complex.
        # Actually, let's try to iterate nicely if possible, or just use a known trick.
        # Simple approach: Return a placeholder that says "Recycle Bin" and we use a different method to clean.
        # BUT, standard python 'winshell' allows iterating.
        
        files_found = []
        items = []
        total_size = 0
        
        try:
            # winshell.recycle_bin() returns an iterator of deleted items
            for item in winshell.recycle_bin():
                 # item.original_filename(), item.size()
                 path = f"[Recycle Bin] {item.original_filename()}"
                 size = item.size()
                 files_found.append(path)
                 items.append({'path': path, 'size': size})
                 total_size += size
        except Exception:
             # Fallback or permission issues
             pass

        return {
            'files': files_found,
            'items': items,
            'size': total_size,
            'skipped_recent': 0,
            'skipped_recent_size': 0,
        }
        
    def scan_prefetch(self, min_age_days=None):
        if not is_admin():
            return {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}
            
        system_root = os.environ.get('SystemRoot')
        if not system_root:
            return {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

        prefetch_path = os.path.join(system_root, 'Prefetch')
        return self._generic_scan(prefetch_path, extensions=['.pf'], min_age_days=min_age_days)

    def scan_windows_update_cache(self, min_age_days=None):
        if not is_admin():
            return {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

        system_root = os.environ.get('SystemRoot')
        if not system_root:
            return {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

        update_path = os.path.join(system_root, 'SoftwareDistribution', 'Download')
        return self._generic_scan(update_path, min_age_days=min_age_days)

    def scan_thumbnail_cache(self, min_age_days=None):
        local_app_data = os.environ.get('LOCALAPPDATA')
        if not local_app_data:
            return {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

        cache_path = os.path.join(local_app_data, 'Microsoft', 'Windows', 'Explorer')

        def _thumb_predicate(name):
            lowered = name.lower()
            return lowered.startswith('thumbcache_') or lowered.startswith('iconcache_')

        return self._generic_scan(cache_path, name_predicate=_thumb_predicate, min_age_days=min_age_days)

    def scan_shader_cache(self, min_age_days=None):
        local_app_data = os.environ.get('LOCALAPPDATA')
        if not local_app_data:
            return {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

        results = []
        for folder in ['D3DSCache', 'D3DCache']:
            cache_path = os.path.join(local_app_data, folder)
            results.append(self._generic_scan(cache_path, min_age_days=min_age_days))

        return self._merge_results(results) if results else {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

    def scan_error_reports(self, min_age_days=None):
        results = []

        program_data = os.environ.get('ProgramData')
        if program_data:
            sys_wer = os.path.join(program_data, 'Microsoft', 'Windows', 'WER')
            results.append(self._generic_scan(sys_wer, min_age_days=min_age_days))

        local_app_data = os.environ.get('LOCALAPPDATA')
        if local_app_data:
            user_wer = os.path.join(local_app_data, 'Microsoft', 'Windows', 'WER')
            results.append(self._generic_scan(user_wer, min_age_days=min_age_days))

        return self._merge_results(results) if results else {'files': [], 'items': [], 'size': 0, 'skipped_recent': 0, 'skipped_recent_size': 0}

    def scan_selected(self, selected_categories, progress_cb=None, min_age_days=None):
        results = {}
        total = len(selected_categories)
        for idx, cat in enumerate(selected_categories, start=1):
            if cat not in self.categories:
                continue
            try:
                results[cat] = self.categories[cat](min_age_days=min_age_days)
            except Exception as exc:
                results[cat] = {'files': [], 'items': [], 'size': 0, 'error': str(exc), 'skipped_recent': 0, 'skipped_recent_size': 0}
            if progress_cb:
                try:
                    progress_cb(idx, total, cat, results[cat])
                except Exception:
                    # Progress callbacks should never break scans
                    pass

        self.scan_results = results
        return results

    def scan_all(self, min_age_days=None):
        return self.scan_selected(self.categories.keys(), min_age_days=min_age_days)
