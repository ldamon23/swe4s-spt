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
from PIL import Image
import csv

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
    img.iter_axes = 'z'  # t (time) oddly does not work; z-steps instead

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


def process_image(file_name, blurIter=1, gBlur=True, tif_stack=True,
                  subBg=True, detectEdges=True, out_name='out_processed.tif'):
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
            images = read_tif(file_name)
            for i in range(len(images)):
                img = images[i]
                if gBlur:
                    img = cv.GaussianBlur(img, (5, 5), blurIter)
                if subBg:
                    img = subtract_background(img)
                if detectEdges:
                    img = cv.Laplacian(img, cv.CV_64F)
                    img = np.uint16(np.absolute(img))
                print('.', end='')
                results.append(img)
        except FileNotFoundError:
            print("Could not find file " + file_name)
            sys.exit(1)
        finally:
            with TiffWriter(out_name) as tif:
                for frame in results:
                    tif.save(frame, contiguous=True)
    else:
        print('Only tif stacks are supported currently')
        sys.exit(1)

    return results


def extract_features(data, out_name='out_features.tif'):
    '''
    data - list of frames to process should be numpy arrays

    returns an array of arrays that each contain
                (frame id, feature position(x, y), feature size)
    '''
    if data is None:
        print('No data passed to detect features.')
        sys.exit(1)
    results = []
    params = cv.SimpleBlobDetector_Params()
    params.minArea = 0
    params.maxArea = 10000
    detector = cv.SimpleBlobDetector_create(params)
    i = 0
    out_frames = []
    for frame in data:
        # Detect blobs by thresholding converting to 8bit and using cv blob detector.
        ret, thresh = cv.threshold(frame, 5, 100, cv.THRESH_BINARY)
        img8 = thresh.astype('uint8')
        keypoints = detector.detect(img8)
        out = frame
        for kp in keypoints:
            results.append([i, kp.pt, kp.size])
            cv.circle(out, (int(kp.pt[0]), int(kp.pt[1])), int(kp.size), (255, 0 ,0), 2)
            out_frames.append(out)
        i = i + 1

    with TiffWriter(out_name) as tif:
        for frame in out_frames:
            tif.save(frame, contiguous=True)

    return results


def read_tif(path):
    """
    path - Path to the multipage-tiff file
    """
    img = Image.open(path)
    images = []
    for i in range(img.n_frames):
        img.seek(i)
        images.append(np.array(img))

    return np.array(images)


def write_csv(data, file_name='results.csv'):
    '''
    data - list of arrays containing row values
    file_name - default: 'out/result.csv' output file name
    
    writes a csv with given file name and data
    '''
    with open(file_name, mode='w') as csv_file:
        try:
            for row in data:
                wr = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                wr.writerow(row)
        except FileNotFoundError:
            print('Could not open subdirectory \'out\'')
            sys.exit(1)

def subtract_background(img):
    '''
    uses image analysis algorithms to subtract background from frames
    '''
    backSub = cv.createBackgroundSubtractorMOG2()
    img = backSub.apply(img)
    return img


def calc_diffusion(file_in, file_out, query_column,
                   result_columns, traj_ID='all', deltaT=0.1):
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
