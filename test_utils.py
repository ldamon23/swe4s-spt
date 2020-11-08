""" Unit testing of open_file

"""

import unittest
import utils
import sys
import matplotlib.pyplot as plt
import tifffile
import os
from nd2reader import ND2Reader


class TestUtils_utils(unittest.TestCase):
    """ Testing the functionality of functions in utils

    """

#     def test_convert_ND2_missingfile(self):
#         # check for missing file, throw an error

#         file_in = 'crapFile.nd2'
#         file_out = 'crapFile.tif'
#         frame_range = [0]  # load first frame, if possible

#         with self.assertRaises(SystemExit) as ex:
#             utils.convert_ND2(file_in, file_out, frame_range)
#         self.assertEqual(ex.exception.code, 1)

#     def test_convert_ND2_disp_first_frame(self):
#         # check that we can load at minimum one frame

#         file_in = 'sample_SPT.nd2'
#         file_out = 'sample_SPT.tif'
#         frame_range = [0]
#         img = utils.convert_ND2(file_in, file_out, frame_range)

#         self.assertIsNotNone(img)

#     def test_convert_ND2_load_multiple_frames(self):
#         # check that we can load 2+ frames

#         file_in = 'sample_SPT.nd2'
#         file_out = 'sample_SPT.tif'
#         # load first 10 frames - note: indexing starts at 1
#         frame_range = range(0, 10)

#         utils.convert_ND2(file_in, file_out, frame_range)

#         # verify that a file was created and
#         # that it has the specified number of frames
#         file = open('sample_SPT.tif')
#         self.assertIsNotNone(file)
#         file.close

#         tif = tifffile.TiffFile('sample_SPT.tif')
#         self.assertEqual(len(tif.pages), 10)

#     def test_convert_ND2_write_all_frames(self):
#         # check that we can load all frames

#         file_in = 'sample_SPT.nd2'
#         file_out = 'sample_SPT.tif'
#         frame_range = 'all'  # load all frames

#         utils.convert_ND2(file_in, file_out, frame_range)

#         # verify that a file was created and
#         # that it has the specified number of frames
#         file = open(file_out)
#         self.assertIsNotNone(file)
#         file.close()

#         img = ND2Reader(file_in)
#         total_frames = (img.sizes['z'])

#         tif = tifffile.TiffFile('sample_SPT.tif')
#         self.assertEqual(len(tif.pages), total_frames)

    def test_process_image(self):
        # check that process image is taking in a tif stack and
        # then processing that tif stack

        file_in = 'sample_SPT.tif'
        file_out = 'out/result.tif'
        result = None
        try:
            os.mkdir('out/')
        except FileExistsError:
            pass
        result = utils.process_image(file_in, subBg=False)
        self.assertIsNotNone(result)

        file = open(file_out)
        self.assertIsNotNone(file)
        file.close()


if __name__ == '__main__':
    unittest.main()
