""" Unit testing of open_file

"""

import unittest
import utils
import sys
import matplotlib.pyplot as plt

class TestUtils_utils(unittest.TestCase):
    """ Testing the functionality of functions in utils

    """

    def test_convert_ND2_missingfile(self):
        # check for missing file, throw an error

        file_in = 'crapFile.nd2'
        file_out = 'crapFile.tif'
        frame_range = [0]

        with self.assertRaises(SystemExit) as ex:
           utils.convert_ND2(file_in, file_out, frame_range)
        self.assertEqual(ex.exception.code, 1)

    def test_convert_ND2_disp_first_frame(self):
        # check that we can load at minimum one frame
        
        file_in = 'sample_SPT.nd2'
        file_out = 'sample_SPT.tif'
        frame_range = [0]
        img = utils.convert_ND2(file_in, file_out, frame_range)
        
        self.assertIsNotNone(img)

        
if __name__ == '__main__':
    unittest.main()
