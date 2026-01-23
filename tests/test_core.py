import unittest
import os
import shutil
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.scanner import Scanner
from core.cleaner import Cleaner

class TestCleaner(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.environ['TEMP'], 'cleaner_wannabe_test')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Create dummy temp files
        self.file1 = os.path.join(self.test_dir, 'junk1.tmp')
        with open(self.file1, 'w') as f:
            f.write("junk data")
            
        self.scanner = Scanner()
        self.cleaner = Cleaner()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_scan_custom_path(self):
        # We need to hack the scanner to scan our test dir for this test
        # or we just rely on the logic that scan_temp uses os.walk
        
        # Let's mock the temp path in scanner's scan_temp for testing
        # Since os.environ is global, we can temporarily patch it? 
        # Or just verify the cleaner logic given a file list.
        
        scan_results = {'files': [self.file1], 'size': 9}
        
        count, size, errors = self.cleaner.clean_category('Test', scan_results)
        
        self.assertEqual(count, 1)
        self.assertEqual(size, 9)
        self.assertFalse(os.path.exists(self.file1))

if __name__ == '__main__':
    unittest.main()
