""" Get Diffusion Coeffs

With a CSV file as an output, calculate diffusion coefficients for
single particle trajectories

"""

import utils
import argparse
import csv
import matplotlib.pyplot as plt
import sys


def main():

    """ Main function for getting diffusion

    Arguements are defined at the command line via argparse

    utils.calc_diffusion  : Calculate diffusion coeffs

    """
    # initialize argparser

    parser = argparse.ArgumentParser(description='Get a column from a file')

    parser.add_argument('--file',
                        dest='file_in',
                        type=str,
                        required=True,
                        help="File to be processed")
    parser.add_argument('--delta_T',
                        dest='deltaT',
                        type=str,
                        required=True,
                        help="Time delay between frames, in seconds")
    args = parser.parse_args()

    # set-up
    file_in = args.file_in
    file_out = file_in[:-4] + '_diffusion_coeffs.csv'
    traj_ID = 'all'  # compute all diffusion coeffs; default
    query_column = 1
    result_columns = [3, 4]
    deltaT = args.deltaT  # exposure time, in seconds

    traj_xy, diffusion = utils.calc_diffusion(file_in,
                                              query_column,
                                              result_columns,
                                              traj_ID,
                                              deltaT)

    # write diffusion coeffs to CSV
    field_names = ['Trajectory_ID', 'Diffusion_Coeff (um^2/s)']

    with open(file_out, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the fields and data
        csvwriter.writerow(field_names)
        csvwriter.writerows(diffusion)

    # plot histogram of diffusion coeffs
    hist_out_file = file_in[:-4] + '_diffusion_coeffs_hist.png'
    # diffusion stored as list of lists; need to make array
    diff_coeffs = [diff_coeff for ID, diff_coeff in diffusion]
    width = 3
    height = 3
    fig = plt.figure(figsize=(width, height), dpi=300)

    ax = fig.add_subplot(1, 1, 1)

    ax.hist(diff_coeffs)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.savefig(hist_out_file, bbox_inches='tight')


if __name__ == '__main__':

    main()
