""" Unit testing of utils

"""

import unittest
import utils
import sys
import matplotlib.pyplot as plt
import tifffile
from nd2reader import ND2Reader


class TestUtils_convert_ND2(unittest.TestCase):
    """ Testing the functionality of convert_ND2

    """

    def test_convert_ND2_missingfile(self):
        # check for missing file, throw an error

        file_in = 'crapFile.nd2'
        file_out = 'crapFile.tif'
        frame_range = [0]  # load first frame, if possible

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
        # load first 10 frames - note: indexing starts at 1
        frame_range = range(0, 10)

        utils.convert_ND2(file_in, file_out, frame_range)

        # verify that a file was created and
        # that it has the specified number of frames
        file = open('sample_SPT.tif')
        self.assertIsNotNone(file)
        file.close

        tif = tifffile.TiffFile('sample_SPT.tif')
        self.assertEqual(len(tif.pages), 10)

    def test_convert_ND2_write_all_frames(self):
        # check that we can load all frames

        file_in = 'sample_SPT.nd2'
        file_out = 'sample_SPT.tif'
        frame_range = 'all'  # load all frames

        utils.convert_ND2(file_in, file_out, frame_range)

        # verify that a file was created and
        # that it has the specified number of frames
        file = open(file_out)
        self.assertIsNotNone(file)
        file.close()

        img = ND2Reader(file_in)
        total_frames = (img.sizes['z'])

        tif = tifffile.TiffFile('sample_SPT.tif')
        self.assertEqual(len(tif.pages), total_frames)

    def test_process_image(self):
        # check that process image isn't throwing any errors

        file_in = 'sample_SPT.tif'
        file_out = 'out/9.png'
        result = None
        result = utils.process_image(file_in)
        self.assertIsNotNone(result)

        file = open(file_out)
        self.assertIsNotNone(file)
        file.close()
        

class TestUtils_calc_diffusion(unittest.TestCase):
    """ Testing the functionality of the function calc_diffusion

    """

    def test_calc_diffusion_missingfile(self):
        # check for missing file, throw an error

        file_in = 'crapFile.csv'  # I'm assuming I'll have a CSV, similar to mosaic
        file_out = file_in[:-4] + '_diffusion_coeffs.csv'
        traj_ID = 1
        query_column = 1
        results_columns = [3, 4]

        with self.assertRaises(SystemExit) as ex:
           utils.calc_diffusion(file_in, file_out, query_column, traj_ID, results_columns)
        self.assertEqual(ex.exception.code, 1)
        
    def test_calc_diffusion_look_at_single_traj(self):
        # identify a single trajectory, maybe pull out X-Y coords?

        file_in = 'sample_traj.csv'  # I'm assuming I'll have a CSV, similar to mosaic
        file_out = file_in[:-4] + '_diffusion_coeffs.csv'
        traj_ID = 1
        query_column = 1
        result_columns = [3, 4]
        deltaT = 0.1  # exposure time, in seconds

        traj_xy, diffusion = utils.calc_diffusion(file_in, file_out, query_column, result_columns, traj_ID, deltaT)
        
        expected = [['170.202', '22.481'], 
                    ['169.726', '22.459'], 
                    ['169.192', '22.727'],
                    ['165.640', '22.686']]

        self.assertEqual(traj_xy, expected)
    
    def test_calc_diffusion_get_diffusion_single_traj(self):
        # compute the diffusion coefficient for a trajectory
        
        file_in = 'sample_traj.csv'  # I'm assuming I'll have a CSV, similar to mosaic
        file_out = file_in[:-4] + '_diffusion_coeffs.csv'
        traj_ID = 1
        query_column = 1
        result_columns = [3, 4]
        deltaT = 0.1  # exposure time, in seconds

        traj_xy, diffusion = utils.calc_diffusion(file_in, file_out, query_column, result_columns, traj_ID, deltaT)
        
        self.assertIsNotNone(diffusion)
        # not sure what a better test would be for this...

    def test_calc_diffusion_look_at_all_tracks(self):
        # compute the diffusion coefficients for all trajectories

        file_in = 'sample_traj_crop.csv'  # cropped file to minimize runtime
        file_out = file_in[:-4] + '_diffusion_coeffs.csv'
        traj_ID = 'all'
        query_column = 1
        result_columns = [3, 4]
        deltaT = 0.1  # exposure time, in seconds

        traj_xy, diffusion = utils.calc_diffusion(file_in, file_out, query_column, result_columns, traj_ID, deltaT)
        
        self.assertEqual(len(diffusion),4)
        # similar to the above test, I don't know what a better test would be


if __name__ == '__main__':
    unittest.main()
