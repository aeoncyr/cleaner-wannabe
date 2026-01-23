import unittest
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.cleaner import Cleaner
from core.safety import SafetyManager

class TestSafety(unittest.TestCase):
    def setUp(self):
        self.cleaner = Cleaner()
        # Mock the safety manager's methods to avoid actual IO/System calls
        self.cleaner.safety.log_action = MagicMock()
        self.cleaner.safety.log_error = MagicMock()
        self.cleaner.safety.create_restore_point = MagicMock(return_value=(True, "Mocked Restore Point"))

    @patch('core.cleaner.send2trash.send2trash')
    @patch('os.remove')
    def test_safe_mode_recycle_bin(self, mock_remove, mock_send2trash):
        # Create a dummy file entry
        files = ['C:\\dummy\\junk.tmp']
        
        # Test Safe Mode = True
        with patch('os.path.isfile', return_value=True), patch('os.path.getsize', return_value=100):
            self.cleaner.clean_files(files, use_recycle_bin=True)
            
            mock_send2trash.assert_called_once_with('C:\\dummy\\junk.tmp')
            mock_remove.assert_not_called()
            self.cleaner.safety.log_action.assert_called()

    @patch('core.cleaner.send2trash.send2trash')
    @patch('os.remove')
    def test_normal_mode_delete(self, mock_remove, mock_send2trash):
        files = ['C:\\dummy\\junk.tmp']
        
        # Mock os.path defaults
        with patch('os.path.isfile', return_value=True), patch('os.path.getsize', return_value=100):
            # Test Safe Mode = False
            self.cleaner.clean_files(files, use_recycle_bin=False)
            
            mock_remove.assert_called_once_with('C:\\dummy\\junk.tmp')
            mock_send2trash.assert_not_called()

    def test_restore_point_call(self):
        self.cleaner.run_safety_checks()
        self.cleaner.safety.create_restore_point.assert_called_once()

if __name__ == '__main__':
    unittest.main()
