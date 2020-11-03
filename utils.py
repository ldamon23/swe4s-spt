""" Utilty functions for SPT project
"""

import sys
import sys
import numpy as np
from nd2reader import ND2Reader
import matplotlib.pyplot as plt
import tifffile

# from PIL import Image
# import sys
# import numpy as np
# from nd2reader import ND2Reader
# import matplotlib.pyplot as plt
# import tifffile

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
    except:
        print("Could not find file " + file_in)
        sys.exit(1)

    img = ND2Reader(file_in)
    img.iter_axes = 'z' # t oddly does not work; z-steps instead
    
    # handle cases where we want to process all frames
    if frame_range == 'all':
        frame_range = range(img.sizes['z'])
    
    for index, frame in enumerate(frame_range):
        if index == 0:
            print('Curr frame is: ' + str(frame))
            output_img = np.array(img[frame], dtype='uint16')
            tifffile.imwrite(file_out, output_img)
        else:
            print('Curr frame is: ' + str(frame))
            output_img = np.array(img[frame], dtype='uint16')  # take frame and store as np array
            tifffile.imwrite(file_out, output_img, append=True)

    return output_img


    
