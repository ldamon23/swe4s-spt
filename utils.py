""" Utilty functions for SPT project
"""

import sys
import subprocess
try:
    import cv2 as cv
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m",
                           "pip", "install", 'opencv-contrib-python'])
    import cv2 as cv
import numpy as np
try:
    from nd2reader import ND2Reader
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m",
                           "pip", "install", 'nd2reader'])
    from nd2reader import ND2Reader
import matplotlib.pyplot as plt
import tifffile
from tifffile import *
from skimage import io
import pims
# from PIL import Image


def convert_ND2(file_in, file_out, frame_range='all'):
    """ Because ND2s are a pain to work with, convert to TIF

    Parameters:
    file_in     : ND2 image to be processed
    file_out    : Name of the output TIF
    frame_range : Frame range to iterate over; defaults to 'all'

    outputs:
    img_out    : converted TIF file
    """

    # check that the file exists
    try:
        img = ND2Reader(file_in)
    except FileNotFoundError:
        print("Could not find file " + file_in)
        sys.exit(1)

    img.iter_axes = 'z'  # t oddly does not work; z-steps instead

    # handle cases where we want to process all frames
    if frame_range == 'all':
        frame_range = range(img.sizes['z'])

    for index, frame in enumerate(frame_range):
        if index == 0:
            print('Processing frames[0.', end='')
            output_img = np.array(img[frame], dtype='uint16')
            tifffile.imwrite(file_out, output_img)
        else:
            print('.', end='')
            # take frame and store as np array
            output_img = np.array(img[frame], dtype='uint16')
            tifffile.imwrite(file_out, output_img, append=True)
    print('.' + str(frame) +
          ']     Done. Curr frame is: ' +
          str(frame) + '    ')
    img.close()

    return output_img


def process_image(file_name, blurIter=1, gBlur=True, tif_stack=True, subBg=True):
    '''Use image analysis algorithms to extract features from an image

    Parameters:
    file_name    :name of the file to be processed
    tif_stack     :decides whether to process image as a tif stack
    blurIter    :# of iterations the gaussian blur should be applied
    gBlur    :boolean decider for gaussian blur application
    tif_stack    :boolean decider to handle file as a tif stack

    Outputs:
    results    :list of processed frames from the video
    '''
    results = []
    if tif_stack:
        try:
            with pims.TiffStack(file_name) as images:
                for i in range(len(images)):
                    img = images[i]
                    if gBlur:
                        img = cv.GaussianBlur(img, (5, 5), blurIter)
                    if subBg:
                        backSub = cv.createBackgroundSubtractorKNN()
                        img = backSub.apply(img)
                    print('.', end='')
                    results.append(img)
        except FileNotFoundError:
            print("Could not find file " + file_name)
            sys.exit(1)
    else:
        print('Only tif stacks are supported currently')
        sys.exit(1)
    with TiffWriter('out/result.tif') as tif:
        for frame in results:
            tif.save(frame, contiguous=True)
    return results
