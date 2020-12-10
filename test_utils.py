""" Unit testing of utils

"""
import utils
import unittest
import sys
import matplotlib.pyplot as plt
import tifffile
import os
from nd2reader import ND2Reader
import cv2 as cv


# class TestUtils_convert_ND2(unittest.TestCase):
#     """ Testing the functionality of convert_ND2

#     """

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


# class TestUtils_calc_diffusion(unittest.TestCase):
#     """ Testing the functionality of the function calc_diffusion

#     """

#     def test_calc_diffusion_missingfile(self):
#         # check for missing file, throw an error

#         file_in = 'crapFile.csv'  # I'm assuming I'll have a CSV
#         traj_ID = 1
#         query_column = 1
#         results_columns = [3, 4]

#         with self.assertRaises(SystemExit) as ex:
#             utils.calc_diffusion(file_in,
#                                  query_column,
#                                  traj_ID,
#                                  results_columns)
#         self.assertEqual(ex.exception.code, 1)

#     def test_calc_diffusion_look_at_single_traj(self):
#         # identify a single trajectory, maybe pull out X-Y coords?

#         file_in = 'sample_traj.csv'  # I'm assuming I'll have a CSV
#         file_out = file_in[:-4] + '_diffusion_coeffs.csv'
#         traj_ID = 1
#         query_column = 1
#         result_columns = [3, 4]
#         deltaT = 0.1  # exposure time, in seconds

#         traj_xy, diffusion = utils.calc_diffusion(file_in,
#                                                   query_column,
#                                                   result_columns,
#                                                   traj_ID,
#                                                   deltaT)

#         expected = [['170.202', '22.481'],
#                     ['169.726', '22.459'],
#                     ['169.192', '22.727'],
#                     ['165.640', '22.686']]

#         self.assertEqual(traj_xy, expected)

#     def test_calc_diffusion_get_diffusion_single_traj(self):
#         # compute the diffusion coefficient for a trajectory

#         file_in = 'sample_traj.csv'  # I'm assuming I'll have a CSV
#         traj_ID = 1
#         query_column = 1
#         result_columns = [3, 4]
#         deltaT = 0.1  # exposure time, in seconds

#         traj_xy, diffusion = utils.calc_diffusion(file_in,
#                                                   query_column,
#                                                   result_columns,
#                                                   traj_ID,
#                                                   deltaT)

#         self.assertIsNotNone(diffusion)
#         # not sure what a better test would be for this...

#     def test_calc_diffusion_look_at_all_tracks(self):
#         # compute the diffusion coefficients for all trajectories

#         file_in = 'sample_traj_crop.csv'  # cropped file to minimize runtime
#         file_out = file_in[:-4] + '_diffusion_coeffs.csv'
#         traj_ID = 'all'
#         query_column = 1
#         result_columns = [3, 4]
#         deltaT = 0.1  # exposure time, in seconds

#         traj_xy, diffusion = utils.calc_diffusion(file_in,
#                                                   query_column,
#                                                   result_columns,
#                                                   traj_ID,
#                                                   deltaT)

#         self.assertEqual(len(diffusion), 4)


# class TestUtils_calc_dwelltime(unittest.TestCase):
#     """
#     Tests for calculating particle dwell times
#     """

#     def test_calc_dwelltime_dataexists(self):
#         # check that we can read in some data

#         # create some arbitrary xy coordinates (units in nm)
#         some_xy = [['170.202', '22.481'],
#                    ['169.726', '22.459'],
#                    ['169.192', '22.727'],
#                    ['165.640', '22.686']]
#         max_disp = 200  # max displacement between frames; units in nm
#         min_bound_frames = 2  # min number of frames to be considered bound
#         frame_rate = 0.1  # in seconds

#         # calc & print dwell time
#         dwell_time = utils.calc_dwelltime(some_xy,
#                                           max_disp,
#                                           min_bound_frames,
#                                           frame_rate)
#         self.assertEqual(dwell_time, [4*frame_rate])

#         # can we handle tracks with multiple binding events?
#         some_xy = [['3', '3'],
#                    ['3', '4'],
#                    ['3', '5'],
#                    ['4', '6'],
#                    ['5', '4'],
#                    ['100', '100'],
#                    ['200', '200'],
#                    ['250', '250'],
#                    ['251', '251'],
#                    ['251', '252'],
#                    ['251', '253'],
#                    ['300', '300'],
#                    ['350', '350']]
#         max_disp = 5  # units in nm
#         min_bound_frames = 2
#         frame_rate = 0.1  # in seconds

#         dwell_time = utils.calc_dwelltime(some_xy,
#                                           max_disp,
#                                           min_bound_frames,
#                                           frame_rate)
#         self.assertEqual(dwell_time, [5*frame_rate, 4*frame_rate])

#         # can we handle no binding events?
#         some_xy = [['3', '3'],
#                    ['3', '40'],
#                    ['3', '80'],
#                    ['4', '120'],
#                    ['5', '160'],
#                    ['100', '200'],
#                    ['200', '240'],
#                    ['250', '280'],
#                    ['251', '320'],
#                    ['251', '360'],
#                    ['251', '400'],
#                    ['300', '440'],
#                    ['350', '480']]
#         max_disp = 5  # units in nm
#         min_bound_frames = 2
#         frame_rate = 0.1  # in seconds

#         dwell_time = utils.calc_dwelltime(some_xy,
#                                           max_disp,
#                                           min_bound_frames,
#                                           frame_rate)
#         # self.assertEqual(dwell_time, [])
#         # note - the above is a bad test/comparison. [] is not the same as None
#         # and I ran into issues later when trying to pull out values for
#         # plotting.

#         self.assertEqual(dwell_time, None)  # this is better


# class TestUtils_get_xy_coords(unittest.TestCase):
#     '''
#     Tests to develop a function to extract xy coordinates for a track
#     '''

#     def test_get_xy_coords(self):
#         # check that I can extract xy coords
#         # note this function is basically the beginning of calc_diffusion, so
#         # minimal testing should be needed :)

#         file_in = 'sample_traj_crop.csv'
#         query_column = 1
#         result_columns = [3, 4]
#         traj_ID = 1

#         xy_coords = utils.get_xy_coords(file_in,
#                                         query_column,
#                                         result_columns,
#                                         traj_ID)
#         expected = [[170.202, 22.481],
#                     [169.726, 22.459],
#                     [169.192, 22.727],
#                     [165.64, 22.686]]
#         self.assertEqual(xy_coords, expected)


class TestUtils_process_image(unittest.TestCase):
    '''
    Tests for the functionality of image processing
    Will test image processing and feature extraction
    '''
    def setUp(self):
        # create test files in case they are not yet created
        file_in = 'sample_SPT.nd2'
        file_out = 'sample_SPT.tif'
        try:
            file = open(file_out)
        except FileNotFoundError:
            utils.convert_ND2(file_in, file_out, 'all')
            utils.process_image(file_out, blurIter=2)
        file.close()
        
    def test_image_processing(self):
        # check that process image is taking in a tif stack and
        # then processing and saving that tif stack

        file_in = 'sample_SPT.tif'
        file_out = 'out_processed.tif'
        result = None
        result = utils.process_image(file_in, blurIter=2)
        cv.waitKey(1000)  #wait for the file to be closed
        self.assertIsNotNone(result)

        file = open(file_out)
        self.assertIsNotNone(file)
        file.close()

    def test_feature_extraction(self):
        # check that features are being extracted
        # correctly from the processed tif stack
        file_in = 'out_processed.tif'
        # get the frames to be processed as np arrays
        processed_frames = utils.read_tif(file_in)
        # shrink the test set for optimization
        frames = processed_frames[1:20]
        features = None
        # extract features will save a result.tif with keypoints
        features = utils.extract_features(frames)
        self.assertIsNotNone(features)
        # the results csv should contain predictable values
        utils.write_csv(features)
#         self.assertEqual(int(features[8][1][1]), 88)

        file = open('out_features.tif')
        self.assertIsNotNone(file)
        file.close()

class TestUtils_track_linking(unittest.TestCase):
    '''
    Tests for the functionality of track linking
    using process image output data
    '''
    def test_track_csv(self):
    # check that track csv is working properly
        utils.track_csv()
    
if __name__ == '__main__':
    unittest.main()
