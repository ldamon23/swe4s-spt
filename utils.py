""" 
Utilty functions for SPT project

Functions include:
convert_ND2()      - Conversion of ND2 files to tif stacks
read_tif()               - Reading of tif stacks as a list of numpy arrays
process_image()    - Processing of numpy arrays using computer vision
extract_features()  - Extraction of signal features from numpy arrays
write_csv()            - Writing custom CSV files given arrays of data
calc_diffusion()     - Calculates diffusion coefficient
                                 from extracted signal features
"""

import sys
from nd2reader import ND2Reader
import cv2 as cv  # computer vision library
import numpy as np
import tifffile
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


def process_image(file_name, blurIter=1, gBlur=True,
                  out_name='out_processed.tif'):
    '''Use image analysis algorithms to clean up signal from images

    Requirements:
    The image must be a tif stack as of now

    Algorithms used:
    Gaussian Blur -
    Laplacian -

    Definitions:
    tif stack: A virtual stack of tagged image files (tif) images 
                 : in this case it is likely to be a timeseries of fluorescence data

    Parameters:
    file_name    :string: Name of the file to be processed
    blurIter    :integer: Number of iterations the gaussian blur should be applied
    gBlur    :boolean: Decider for gaussian blur application

    Outputs:
    results    :List of numpy arrays (frames) extracted from the given video file
    '''
    results = []

    try:
        images = read_tif(file_name)
        for i in range(len(images)):
            img = images[i]
            if gBlur:
                img = cv.GaussianBlur(img, (5, 5), blurIter)
            img = cv.Laplacian(img, cv.CV_64F)
            img = np.uint16(np.absolute(img))  #convert back to 16bit to save as a readable tif stack
            print('.', end='')
            results.append(img)
    except FileNotFoundError:
        print("Could not find file " + file_name)
        sys.exit(1)
    finally:
        with tifffile.TiffWriter(out_name) as tif:  # may want to refactor is used twice
            for frame in results:
                tif.save(frame, contiguous=True)


    return results


def extract_features(data, out_name='out_features.tif'):
    '''
    Ues opencv blob detection to find features from numpy arrays
    
    Inputs:
    data - List of numpy arrays (frames)

    Outputs:
    results    :Array of arrays with structure as follows
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
        # Ret is a return that is the threshold used.
        ret, thresh = cv.threshold(frame, 5, 100, cv.THRESH_BINARY)
        img8 = thresh.astype('uint8')
        keypoints = detector.detect(img8)
        out = frame
        for kp in keypoints:
            results.append([i, kp.pt, kp.size])
            cv.circle(out, (int(kp.pt[0]), int(kp.pt[1])), int(kp.size), (255, 0 ,0), 2)
            out_frames.append(out)
        i = i + 1

    with tifffile.TiffWriter(out_name) as tif:
        for frame in out_frames:
            tif.save(frame, contiguous=True)

    return results


def read_tif(path):
    """
    Read a tif stack and return numpy arrays
    
    Inputs:
    path - :string: Path to the tif stack 
    
    Returns:
    a numpy array of numpy arrays (tif stack frames)
    
    """
    img = Image.open(path)
    images = []
    for i in range(img.n_frames):
        img.seek(i)
        images.append(np.array(img))

    return np.array(images)


def write_csv(data, file_name='results.csv'):
    '''
    Write a simple CSV file with given data and name
    
    Inputs:
    data - :list of arrays: Contains row values
    file_name - :string:  Output file name
                        default - 'out/result.csv' 
    
    Output:
    No return
    Will write a CSV saving as file name with given data
    '''
    with open(file_name, mode='w') as csv_file:
        try:
            for row in data:
                wr = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                wr.writerow(row)
        except FileNotFoundError:
            print('Could not open subdirectory \'out\'')
            sys.exit(1)


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

def calc_dwelltime(xydata, max_disp):
    """ Calculate particle dwell time
    
    Inputs:
    ----
    xydata          : list
                      list of xy coordinates for each particle
    max_disp        : int
                      maxium displacement a particle travels between frames
    
    Outputs:
    ----
    dwell_times     : int
                      particle dwell time
    
    """

    boundIdx = {};
    currRow = 1;
    done = false;
    
    while ~done
        
        # for the current row, compute distances from other points
        distVsCurrRow = sqrt(sum((currtrack - currtrack(currRow, :)).^2, 2))
        # find points that are less than the threshold distance)
        bound = [distVsCurrRow < thresholdDistForBound ; false]
        
        # Find series of consecutive ones
        # LJD note: find the first non-zero element in the matrix of Bound - 1 (if it's bound, then it's 1; bound - 1 = 0; unbound-1 = -1
        consecOnes = find(bound(currRow:end) - 1 < 0, 1, 'first')  # ORIGINAl
        
        consecOnes = consecOnes - 1; % LJD edit - modifed 1 from 2 (to get accurate starting point for n consecutive frames;
        % note that this is an array that is currFrame x 1,so indices are relative to that
        
        if consecOnes > minBoundDwellFrames
            
            isBound = true
            currRow = consecOnes + currRow
            
            boundIdx{end + 1} = (currRow - consecOnes):(currRow-1)
            # label each point with its appropriate state
            currBoundLength = length(boundIdx)
            
            boundTracks(end+1) = tracks2plot(gg)
        else
            currRow = currRow + 1;
        
        if currRow >= size(currtrack, 1)
            done = true;


