import os
import sys
import unittest
import pandas as pd

script_dir = os.path.dirname(__file__)
sep_dir = os.path.join(script_dir, '..', 'sep')
sys.path.append(sep_dir)
import sep_aq


class CommonTestCase(unittest.TestCase):
    def test_extract_aq_api(self):
        frame = sep_aq.extract_aq_api.run('Ozone%20(air)')
        self.assertIsNotNone(frame)


if __name__ == '__main__':
    unittest.main()
