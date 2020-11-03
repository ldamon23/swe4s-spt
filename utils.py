""" Utilty functions for SPT project
"""

import sys
import cv2
import numpy as np
from nd2reader import ND2Reader
import matplotlib.pyplot as plt
from PIL import Image
import imageio


def convert_ND2(file_in, file_out, frame_range):
    """ Because ND2s are a pain to work with, convert to TIF
    
    Parameters:
    file_in     : ND2 image to be processed
    file_out    : Name of the output TIF
    
    outputs:
    img_out    : converted TIF file
    """
    
    # check that the file exists
    try:
        img = ND2Reader(file_in)
    except:
        print("Could not find file " + file_in)
        sys.exit(1)

    img = ND2Reader(file_in)
    img.iter_axes = 'z'
    img_dimensions = img.sizes
    xsize = img_dimensions['x']
    ysize = img_dimensions['y']
    tsize = img_dimensions['z']
    final_img = np.zeros((ysize,xsize))
    
    for i in frame_range:
        print('Curr frame is: ' + str(i))
        temp_img = np.asarray(img[i]) # take frame and store as np array
        print(temp_img.shape)
#         np.dstack(final_img, temp_img)
        ### TO DO: figure out why my temp_img array is 1 px wider than what it should be
        # I can't merge np arrays for the final save until this happens... FFFFF

    return final_img
        


    
