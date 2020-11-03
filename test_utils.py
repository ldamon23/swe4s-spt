""" Unit testing of open_file

"""

import unittest
import utils
import sys
import matplotlib.pyplot as plt
import tifffile

class TestUtils_utils(unittest.TestCase):
    """ Testing the functionality of functions in utils

    """

    def test_convert_ND2_missingfile(self):
        # check for missing file, throw an error

        file_in = 'crapFile.nd2'
        file_out = 'crapFile.tif'
        frame_range = [0] # load first frame, if possible

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

    def test_convert_ND2_load_multiple_frames(self):
        # check that we can load 2+ frames
        
        file_in = 'sample_SPT.nd2'
        file_out = 'sample_SPT.tif'
        frame_range = range(0,10)  # load first 10 frames - note: indexing starts at 1
        
        utils.convert_ND2(file_in, file_out, frame_range)
        
        # verify that a file was created and that it has the specified number of frames
        file = open('sample_SPT.tif')
        self.assertIsNotNone(file)
        file.close
        
        tif = tifffile.TiffFile('sample_SPT.tif')
        self.assertEqual(len(tif.pages),10)
        

        
if __name__ == '__main__':
    unittest.main()
