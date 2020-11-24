""" Get Diffusion Coeffs

With a CSV file as an output, calculate diffusion coefficients for
single particle trajectories

"""

import utils
import argparse


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

    args = parser.parse_args()

    # convert file
    file_in = args.file_in
    file_out = file_in[:-4] + '_diffusion_coeffs.csv' # NOTE: currently not used
    traj_ID = 'all'  # compute all diffusion coeffs
    query_column = 1
    result_columns = [3, 4]
    deltaT = 0.1  # exposure time, in seconds

    traj_xy, diffusion = utils.calc_diffusion(file_in, file_out, query_column, result_columns, traj_ID, deltaT)

    print(diffusion)
    
    ## TO DO: plot histogram of trajectory

if __name__ == '__main__':

    main()
