import os
import winreg
import send2trash
import hashlib
import subprocess
from core.utils import format_size

class Analyzer:
    def find_large_files(self, start_path, min_size_mb=100):
        """Scans for files larger than min_size_mb (default 100MB)."""
        large_files = []
        min_size_bytes = min_size_mb * 1024 * 1024
        
        try:
            for root, dirs, files in os.walk(start_path):
                for name in files:
                    try:
                        filepath = os.path.join(root, name)
                        size = os.path.getsize(filepath)
                        if size > min_size_bytes:
                            large_files.append((filepath, size))
                    except (OSError, PermissionError):
                        pass
        except Exception:
            pass
            
        # Sort by size descending
        large_files.sort(key=lambda x: x[1], reverse=True)
        return large_files

    def get_startup_items(self):
        """Retrieves startup programs from HKCU and HKLM."""
        items = []
        locations = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
        ]

        for hkey, path in locations:
            try:
                with winreg.OpenKey(hkey, path, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            items.append({'name': name, 'path': value, 'key': hkey, 'sub_key': path})
                            i += 1
                        except OSError:
                            break
            except OSError:
                continue
                
        return items

    def remove_startup_item(self, item):
        """Removes a startup item from the registry."""
        try:
            key = winreg.OpenKey(item['key'], item['sub_key'], 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, item['name'])
            winreg.CloseKey(key)
            return True, f"Removed {item['name']}"
        except Exception as e:
            return False, str(e)

    def delete_file(self, filepath):
        """Safe delete a file using send2trash."""
        try:
            if os.path.exists(filepath):
                send2trash.send2trash(filepath)
                return True, "Moved to Recycle Bin"
            return False, "File not found"
        except Exception as e:
            return False, str(e)

    def find_duplicates(self, search_path):
        """Finds duplicate files based on content hash."""
        # 1. Group by size
        size_groups = {}
        try:
            for root, dirs, files in os.walk(search_path):
                for name in files:
                    try:
                        filepath = os.path.join(root, name)
                        size = os.path.getsize(filepath)
                        if size < 1024: # Skip very small files
                            continue
                        if size not in size_groups:
                            size_groups[size] = []
                        size_groups[size].append(filepath)
                    except:
                        pass
        except:
            return {}

        # 2. Hash candidates
        duplicates = {} # hash -> [file1, file2]
        
        for size, files in size_groups.items():
            if len(files) < 2:
                continue
            
            # Check full hash
            for fpath in files:
                try:
                    file_hash = self._get_file_hash(fpath)
                    if file_hash not in duplicates:
                        duplicates[file_hash] = []
                    duplicates[file_hash].append(fpath)
                except:
                    pass

        # Filter out unique hashes
        final_dupes = {h: paths for h, paths in duplicates.items() if len(paths) > 1}
        return final_dupes

    def _get_file_hash(self, filepath, block_size=65536):
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read(block_size)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(block_size)
        return hasher.hexdigest()

    def get_installed_programs(self):
        """Scans registry for installed programs."""
        programs = []
        roots = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        for hkey_root, key_path in roots:
            try:
                with winreg.OpenKey(hkey_root, key_path) as key:
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        try:
                            sub_key_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, sub_key_name) as sub_key:
                                try:
                                    name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                    uninstall = winreg.QueryValueEx(sub_key, "UninstallString")[0]
                                    programs.append({'name': name, 'uninstall': uninstall})
                                except OSError:
                                    pass
                        except OSError:
                            continue
            except OSError:
                continue
        
        # Deduplicate by name
        seen = set()
        unique_programs = []
        for p in programs:
            if p['name'] not in seen:
                seen.add(p['name'])
                unique_programs.append(p)
                
        unique_programs.sort(key=lambda x: x['name'])
        return unique_programs

    def uninstall_program(self, uninstall_string):
        """Launches the uninstaller."""
        try:
            # Uninstall strings often contain quotes and arguments
            # easiest way is to let the shell handle it
            subprocess.Popen(uninstall_string, shell=True)
            return True, "Uninstaller launched"
        except Exception as e:
            return False, str(e)
