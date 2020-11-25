""" Get Dwell Time

With a CSV file as the output, calculate particle dwell times for each
trajectory

"""

import utils
import argparse
import numpy as np
import csv
import matplotlib.pyplot as plt
import time

def main():

    """ Main function for getting diffusion

    Arguements are defined at the command line via argparse

    utils.calc_diffusion  : Calculate diffusion coeffs

    """
    # initialize argparser
    start_time = time.gmtime(time.time())
    print('Start time is: ' + str(start_time))
    parser = argparse.ArgumentParser(description='Get a column from a file')

    parser.add_argument('--file',
                        dest='file_in',
                        type=str,
                        required=True,
                        help="File to be processed")
    parser.add_argument('--frame_rate',
                        dest='frame_rate',
                        type=float,
                        required=False,
                        help="Time between frames, in seconds")
    parser.add_argument('--bound_frames',
                        dest='min_bound_frames',
                        type=int,
                        required=True,
                        help="How many frames to consider a particle bound")
    parser.add_argument('--max_disp',
                        dest='max_disp',
                        type=int,
                        required=True,
                        help="Maximum distance a particle can travel to be bound")
    args = parser.parse_args()

    # set-up
    file_in = args.file_in
    query_column = 1  # column where trajectory IDs are located
    result_columns = [3, 4]  # columns where X & Y coords are located
    frame_rate = args.frame_rate  # exposure time, in seconds
    min_bound_frames = args.min_bound_frames
    max_disp = args.max_disp
    file_out = file_in[:-4] + '_dwell_times.csv'

    # first, generate a list of unique trajectories in the file
    try:
        traj_file = open(file_in, 'r') # open file with traj info
    except:
        print("Could not find file " + file_in)
        sys.exit(1)

    header = None
    all_trajs = []  # initialize empty list for trajectory IDs

    # pull out all trajectory IDs
    for line in traj_file:
        if header is None:
            header = line
            continue
        currLine = line.rstrip().split(',')
        all_trajs.append(int(currLine[query_column]))

    # convert to np array to use unique function
    all_trajs = np.array(all_trajs)
    all_trajs_unique = np.unique(all_trajs)  # yields only unique traj IDs

    # now, loop through each trajectory to get its xy coords and then get its
    # dwell time(s)
    all_dwell_times = []  # where to store the final data
    for traj_ID in np.nditer(all_trajs_unique):
        traj_file.seek(0)  # reset file to the beginning!
        xy_coords = utils.get_xy_coords(file_in,
                                        query_column,
                                        result_columns,
                                        traj_ID)
        # now, compute dwell times
        dwell_time = utils.calc_dwelltime(xy_coords,
                                      max_disp,
                                      min_bound_frames,
                                      frame_rate)
        # handle cases where we may have multiple binding events (rare)
        if dwell_time != None:
            if len(dwell_time) > 1:
                for i in range(len(dwell_time)):
                    # generate a new traj ID, using decimal points
                    # note: assumes we'll never have > 10 events
                    temp_traj_ID = float(str(traj_ID) + '.' + str(i+1))
                    all_dwell_times.append([temp_traj_ID, dwell_time[i]])
            else:
                # not doing the below appends a list to the list
                dwell_time = dwell_time[0]
        
        all_dwell_times.append([int(traj_ID), dwell_time])

    # write the data to a file
    field_names = ['Trajectory_ID', 'Dwell_Times (s)']

    with open(file_out, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the fields and data
        csvwriter.writerow(field_names)
        csvwriter.writerows(all_dwell_times)

    # plot the data
    hist_out_file = file_in[:-4] + '_dwell_times_hist.png'
    # dwell times stored as list of lists; need to make array
    dwell_times = [dwell for ID, dwell in all_dwell_times]

    # remove Nones and store
    dwell_time_plot = []
    for i in range(len(dwell_times)):
        if dwell_times[i] != None:
            dwell_time_plot.append(dwell_times[i])
    width=3
    height=3
    fig = plt.figure(figsize=(width,height),dpi=300)

    ax = fig.add_subplot(1,1,1)

    ax.hist(dwell_time_plot)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlabel('Dwell Time (s)')
    ax.set_ylabel('Events')
    plt.savefig(hist_out_file,bbox_inches='tight')
    
    end_time = time.gmtime(time.time())
    print('End time is: ' + str(end_time))
if __name__ == '__main__':

    main()
