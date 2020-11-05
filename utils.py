""" Utilty functions for SPT project
"""

import sys
import sys
import numpy as np
from nd2reader import ND2Reader
import matplotlib.pyplot as plt
import tifffile

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


def calc_diffusion(file_in, file_out, query_column, result_columns, traj_ID='all', deltaT=0.1):  # should change traj_ID to default to 'all' to ensure looping
    
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
#         for traj in range(len(all_trajs_unique)):
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
    
