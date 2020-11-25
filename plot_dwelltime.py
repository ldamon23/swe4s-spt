""" Plot Dwell Time

This script will be useful for plotting existing dwell time files.
The calculation of dwell times, similar to diffusion coefficients, can sometimes
take 10-30 min, depending on how many trajectories are being analyzed. If a user
would rather configure plots on a pre-existing CSV files, they can do so here.

Inputs:
---
dwell_file_in  : str
                 CSV file containing the data

Outputs:
----
hist_file_out  : str
                PNG file to export. Default name is dwell_file_in + '_hist.png'

"""

import csv
import matplotlib.pyplot as plt

def main():

    """ Main function for plotting data

    """

    # set-up
    dwell_file_in = 'sample_traj_dwell_times.csv'
    hist_file_out = dwell_file_in[:-4] + '_hist2.png'

    
    # read the file in
    try:
        file = open(dwell_file_in, 'r') # open file with traj info
    except:
        print("Could not find file " + dwell_file_in)
        sys.exit(1)

    header = None
    dwell_time_plot = []
    
    for line in file:
        if header is None:
            header = line
            continue
        curr_line = line.rstrip().split(',')
        # only store data that is not empty
        if curr_line[1] != '':
            dwell_time_plot.append(float(curr_line[1]))

    file.close()

    # begin plotting
    nbins = 100  # number of bins for hist
    
    width=3
    height=3
    fig = plt.figure(figsize=(width,height),dpi=300)

    ax = fig.add_subplot(1,1,1)

    ax.hist(dwell_time_plot, nbins)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlabel('Dwell Time (s)')
    ax.set_ylabel('Events')
    plt.savefig(hist_file_out,bbox_inches='tight')

if __name__ == '__main__':

    main()


