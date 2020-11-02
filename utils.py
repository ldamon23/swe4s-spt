""" Open file using OpenCV2
"""

import cv2
import numpy as np
from nd2reader import ND2Reader
import matplotlib.pyplot as plt

with ND2Reader('test_SPT.nd2') as images:
    # plt.imshow(images[0])
    print(images.sizes)
    
    images.iter_axes = 'z'
    
    for frame in range(len(images)):
        print('Frame is:' + str(frame))
        plt.imshow(images[frame])
        plt.set_cmap('gray')