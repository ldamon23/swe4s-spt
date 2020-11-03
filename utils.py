""" Utilty functions for SPT project
"""

import sys
import cv2
import numpy as np
from nd2reader import ND2Reader
import matplotlib.pyplot as plt
import warnings

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
    
    for i in range(len(frame_range)):
        plt.imshow(img[i])
#     plt.imshow(img[frame_range])
    # iterate over each frame
    with ND2Reader(file_in) as images:
        print(images.sizes)
        # img = cv2.imshow('image',images[0])
        
#        img = plt.imshow(images[0])
#        img = plt.set_cmap('gray')
#        plt.savefig(file_out, bbox_inches='tight')

        images.iter_axes = 'z'

#         for frame in range(len(images)):
#             print('Frame is:' + str(frame))
#             plt.imshow(images[frame])
#             plt.set_cmap('gray')

    return img
    
    
    
#def open_file_ND2:
#    """ Use ND2Reader if a file is ND2"""
#
#    with ND2Reader('test_SPT.nd2') as images:
#        # plt.imshow(images[0])
#        print(images.sizes)
#        
#        images.iter_axes = 'z'
#        
#        for frame in range(len(images)):
#            print('Frame is:' + str(frame))
#            plt.imshow(images[frame])
#            plt.set_cmap('gray')
#
#def open_file_TIF
#    """ Use CV2 if a file is TIF """


    
