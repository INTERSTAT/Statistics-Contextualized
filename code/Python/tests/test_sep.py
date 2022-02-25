import logging
import os
import sys
import unittest

from prefect import Flow
from prefect.tasks.core.function import FunctionTask

script_dir = os.path.dirname(__file__)
sep_dir = os.path.join(script_dir, '..', 'sep')
common_dir = os.path.join(script_dir, '..', 'common')
sys.path.extend([common_dir, sep_dir])
import sep_aq
import utils

WORK_DIRECTORY = "../../../work/"
conf = utils.get_conf('../sep/sep_conf.py')
logging.basicConfig(filename=WORK_DIRECTORY + 'tests.log', encoding='utf-8', level=logging.DEBUG)


class CommonTestCase(unittest.TestCase):
    def test_extract_aq_api(self):
        pollutant = conf["pollutants"][0]
        # Testing local cache
        frame = sep_aq.extract_aq_eea.run(pollutant, country='France', local=True)
        self.assertIsNotNone(frame)
        # TODO Testing API call

    def test_extract_french_aq(self):
        # We need a Flow because extract_french_aq calls extract_aq_eea
        with Flow('test_aq') as flow:
            frame = sep_aq.extract_french_aq(local=True)
            self.assertEqual(type(frame), FunctionTask)


if __name__ == '__main__':
    unittest.main()
