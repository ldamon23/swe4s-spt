""" Process Images and Extract Features

Simple Python script for pre-processing TIF stacks, identifying features,
and extracting the XY coordinates of these features.

"""

import utils
import cv2 as cv

def main():
    " Main function for processing images and extracting features"

    # first, process the image and save the processed file
    file_in = 'sample_SPT.tif'
    result = utils.process_image(file_in, blurIter=2)
    cv.waitKey(1000)  #wait for the file to be closed

    # next, extract features (XY coordinates for eventual track linking)
    file_in = 'out_processed.tif'
    # get the frames to be processed as np arrays
    processed_frames = utils.read_tif(file_in)
    # extract features will save a result.tif with keypoints
    features = utils.extract_features(processed_frames)
    # write the features to a CSV file
    utils.write_csv(features)

if __name__ == '__main__':

    main()
