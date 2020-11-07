""" Utilty functions for SPT project
"""

import sys
import subprocess
try:
    import cv2 as cv
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m",
                           "pip", "install", 'opencv-python'])
    import cv2 as cv
import numpy as np
from nd2reader import ND2Reader
import matplotlib.pyplot as plt
import tifffile
from skimage import io
import pims


def convert_ND2(file_in, file_out, frame_range='all'):
    """ Because ND2s are a pain to work with, convert to TIF
    
    ND2 is Nikon's proprietary image format. Most image/plotting packages
    can't read the data, so we need to have a function written to convert these
    to a TIF file

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


    # read the image into memory; this generates an img object
    img = ND2Reader(file_in)
    img.iter_axes = 'z' # t (time) oddly does not work; z-steps instead

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


def process_image(file_name, blurIter=1, gBlur=True, tif_stack=True):
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
                    cv.imwrite('out/' + str(i) + '.png', img)
                    results.append(img)
        except FileNotFoundError:
            print("Could not find file " + file_name)
            sys.exit(1)
    else:
        print('Only tif stacks are supported currently')
        sys.exit(1)

    return results


def calc_diffusion(file_in, file_out, query_column, result_columns, traj_ID='all', deltaT=0.1):
    """ Calculate diffusion coefficients of particles
    
    Parameters:
    file_in          : trajectory file to process
    file_out         : file to save (NOTE: currently unused; later version will save to csv)
    query_column     : column containing the trajectory IDS
    result_columns   : columns containing the X and Y coordinates, respectively
    traj_ID          : trajectories to analyze. By default, all are analyzed
    delta_T          : exposure time, in seconds. By default, deltaT=0.1
    
    Outputs:
    dataOut          : X & Y coordinates of the particle for each frame it exists
                       Note: This is likely unnecessary & may bog down processing; will likely
                       edit to remove later
    diffusion_coeffs : A list of lists containing the trajectory ID and its diffusion coefficient
    
    """
    
    # check that the file exists
    try:
        traj_file = open(file_in, 'r') # open file with traj info
    except:
        print("Could not find file " + file_in)
        sys.exit(1)
    
    # begin analyzing trajectories
    
    header = None
    diffusion_coeffs = []  # initialize empty list to store diffusion coeffs

    if traj_ID == 'all':
        all_trajs = []  # initialize empty list for trajectory IDs

        # for loop to pull out all trajectory IDs
        for line in traj_file:
            if header is None:
                header = line
                continue
            currLine = line.rstrip().split(',')
            all_trajs.append(int(currLine[query_column]))

        # convert to np array to use unique function
        all_trajs = np.array(all_trajs)
        all_trajs_unique = np.unique(all_trajs)  # yields only unique traj IDs

        dataOut = []
        for traj in np.nditer(all_trajs_unique):
            traj_file.seek(0)  # reset file to the beginning! otherwise won't loop back
            for line in traj_file:
                if header is None:
                    header = line
                    continue
                currLine = line.rstrip().split(',')
                if currLine[query_column] == str(traj):
                    data = []
                    for j in result_columns:
                        data.append(currLine[j])
                    dataOut.append(data)
        
            # calculate mean squared displacement(MSD) for each trajectory:

            # assuming 2D Brownian diffusion, we can simplify the equation to be:
            # MSD = 4*D*deltaT
            # where D is the diffusion coeff and deltaT is the time delay between frames

            # first, transform dataOut to numpy array to make it easier to index (at least for me)
            # I have a feeling this is a messy way to do it; so I'm open to suggestions on cleaning up!

            dataOut2 = np.array(dataOut)
            xdata = []
            ydata = []
            for i in range(len(dataOut2)):
                xdata.append(float(dataOut2[i,0]))
            for i in range(len(dataOut2)):
                ydata.append(float(dataOut2[i,1]))

            # convert back to np array (can't do below math on a list)
            xdata = np.array(xdata)/1000  # converting from nm to um (convention)
            ydata = np.array(ydata)/1000  # converting from nm to um (convention)
            # now, calculate the displacements
            r = np.sqrt(xdata**2 + ydata**2)
            diff = np.diff(r) #this calculates r(t + dt) - r(t)
            diff_sq = diff**2
            MSD = np.mean(diff_sq)

            # diffusion can now be computed
            # note: this is just the "average" diffusion throughout the length of the track
            # as we're assuming it's Brownian motion (for simplicity). A better way would be to fit
            # to a specific model of diffusion (anomolous/constrained, for instance).. 
            # but for now, simplicity rules
            traj_diff = (MSD)/(4 * deltaT)  # final trajectory diffusion

            # append traj ID and diffusion coeff to final list
            temp = [int(traj), traj_diff]
            diffusion_coeffs.append(temp)
            

    else:
        # analyze a single trajectory
        dataOut = []
        for line in traj_file:
            if header is None:
                header = line
                continue
            currLine = line.rstrip().split(',')
            if currLine[query_column] == str(traj_ID):
                data = []
                for j in result_columns:
                    data.append(currLine[j])
                dataOut.append(data)
    
        # calculate mean squared displacement(MSD) for a single trajectory
        # all equations / workflow are the same as above

        dataOut2 = np.array(dataOut)
        xdata = []
        ydata = []
        for i in range(len(dataOut2)):
            xdata.append(float(dataOut2[i,0]))
        for i in range(len(dataOut2)):
            ydata.append(float(dataOut2[i,1]))

        # convert back to np array (can't do below math on a list)
        xdata = np.array(xdata)/1000  # converting from nm to um (convention)
        ydata = np.array(ydata)/1000  # converting from nm to um (convention)
        # now, calculate the displacements
        r = np.sqrt(xdata**2 + ydata**2)
        diff = np.diff(r) #this calculates r(t + dt) - r(t)
        diff_sq = diff**2
        MSD = np.mean(diff_sq)

        # diffusion can now be computed
        diffusion_coeffs = (MSD)/(4 * deltaT)

    traj_file.close()

    return dataOut, diffusion_coeffs
