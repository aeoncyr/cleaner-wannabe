import unittest
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.analyzer import Analyzer

class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = Analyzer()

    def test_find_large_files(self):
        # Create a dummy large file
        test_dir = "test_large_files"
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
            
        # Create a 1MB file (simulating "large" for test by lowering threshold)
        large_file = os.path.join(test_dir, "big.dat")
        with open(large_file, "wb") as f:
            f.seek(1024 * 1024 - 1)
            f.write(b'\0')
            
        # Scan with low threshold (0.5 MB)
        results = self.analyzer.find_large_files(test_dir, min_size_mb=0.5)
        
        # Cleanup
        os.remove(large_file)
        os.rmdir(test_dir)
        
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0][0], large_file)

    def test_find_duplicates(self):
        test_dir = "test_dupes"
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
            
        # Create two identical files and one different
        f1 = os.path.join(test_dir, "file1.txt")
        f2 = os.path.join(test_dir, "file2.txt")
        f3 = os.path.join(test_dir, "unique.txt")
        
        import shutil
        with open(f1, "wb") as f: f.write(b"contents" * 200) # Ensure > 1KB to pass filter
        shutil.copy(f1, f2)
        with open(f3, "wb") as f: f.write(b"different" * 200)
        
        dupes = self.analyzer.find_duplicates(test_dir)
        
        # Cleanup
        shutil.rmtree(test_dir)
        
        self.assertEqual(len(dupes), 1)
        self.assertEqual(len(list(dupes.values())[0]), 2) # Should match 2 files

    @patch('winreg.OpenKey')
    @patch('winreg.EnumValue')
    def test_get_startup_items(self, mock_enum, mock_open):
        # Simulate registry read
        mock_open.return_value.__enter__.return_value = MagicMock()
        # First call returns an item, second call raises OSError (end of first loop)
        # Third call raises OSError (end of second loop, or empty second loop)
        mock_enum.side_effect = [
            ("TestApp", "C:\\TestApp.exe", 1),
            OSError(),
            OSError()
        ]
        
        items = self.analyzer.get_startup_items()
        
        # It runs for HKCU and HKLM, so if we mock it generically it might be called twice.
        # But our list should at least contain the item from the first successful call.
        self.assertTrue(any(i['name'] == "TestApp" for i in items))

if __name__ == '__main__':
    unittest.main()
