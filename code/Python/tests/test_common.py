import os
import sys
import unittest
import pandas as pd

script_dir = os.path.dirname(__file__)
common_dir = os.path.join(script_dir, '..', 'common')
sys.path.append(common_dir)
import geo_base
import utils


class CommonTestCase(unittest.TestCase):
    def test_convert_coordinates(self):
        test_frame = pd.DataFrame({'x': [-11705274.6374], 'y': [4826473.6922]})
        # The 'run' syntax below avoids an error when running tasks outside a flow
        converted = geo_base.convert_coordinates.run(test_frame, 'x', 'y', 'epsg:3857', 'epsg:4326')
        self.assertEqual(converted.iloc[0]['coord'][0], 43.35695086104039)
        self.assertEqual(converted.iloc[0]['coord'][1], -71.86652837606594)

    def test_get_conf(self):
        conf = utils.get_conf('../sep/sep_conf.py')
        self.assertIsNotNone(conf["pollutants"])


if __name__ == '__main__':
    unittest.main()
