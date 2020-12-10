""" Plot Diffusion Coeffs

This script will be useful for plotting existing diffusion coefficient files.
The calculation of diffusion coefficients can sometimes take ~10 min, depending
on how many trajectories are being analyzed. If a user would rather configure
plots on a pre-existing CSV files, they can do so here.

Inputs:
---
diff_file_in:   str
                CSV file containing the data

Outputs:
----
hist_file_out:  str
                PNG file to export. Default name is diff_file_in + '_hist.png'

"""

import csv
import matplotlib.pyplot as plt
import sys


def main():

    """ Main function for plotting data

    """

    # set-up
    diff_file_in = 'sample_outputs/sample_traj_diffusion_coeffs.csv'
    hist_file_out = diff_file_in[:-4] + '_hist.png'

    # read the file in
    try:
        file = open(diff_file_in, 'r')  # open file with traj info
    except FileNotFoundError:
        print("Could not find file " + diff_file_in)
        sys.exit(1)

    header = None
    diffusion = []

    for line in file:
        if header is None:
            header = line
            continue
        curr_line = line.rstrip().split(',')
        diffusion.append(float(curr_line[1]))

    file.close()

    # begin plotting
    nbins = 300  # number of bins for hist

    width = 8
    height = 3
    fig = plt.figure(figsize=(width, height), dpi=300)

    ax = fig.add_subplot(1, 1, 1)

    ax.hist(diffusion, nbins)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlabel('Diffusion Coeff (um^2/s)')
    ax.set_ylabel('Events')
    plt.xlim([0.0035, 0.0055])  # change as needed
    plt.savefig(hist_file_out, bbox_inches='tight')


if __name__ == '__main__':

    main()
