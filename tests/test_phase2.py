import unittest
import os
import shutil
import sys
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.scanner import Scanner

class TestScannerPhase2(unittest.TestCase):
    def setUp(self):
        self.scanner = Scanner()
        self.scanner.scan_temp = MagicMock(return_value={'files': ['temp'], 'size': 100})
        self.scanner.scan_recycle_bin = MagicMock(return_value={'files': ['bin'], 'size': 50})
        
        # Patch the categories dictionary to use the mocks!
        self.scanner.categories['System Temp'] = self.scanner.scan_temp
        self.scanner.categories['Recycle Bin'] = self.scanner.scan_recycle_bin
        
        # Test selecting only 'System Temp'
        results = self.scanner.scan_selected(['System Temp'])
        self.assertIn('System Temp', results)
        self.assertNotIn('Recycle Bin', results)
        self.scanner.scan_temp.assert_called_once()
        self.scanner.scan_recycle_bin.assert_not_called()

    def test_scan_logs_structure(self):
        # We can't easily mock the filesystem for logs without extensive setup,
        # but we can check if it returns the expected structure even if empty (non-admin)
        result = self.scanner.scan_logs()
        self.assertIn('files', result)
        self.assertIn('size', result)
        
if __name__ == '__main__':
    unittest.main()
