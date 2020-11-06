""" Convert an ND2 file to a TIF 

ND2 is Nikon's proprietary image format. Many image/plotting packages are unable
to unpack these to access the image data; therefore, we need to convert any ND2 file
to a TIF to begin the analysis.

"""

import utils
import argparse


def main():

    """ Main function for converting ND2 file

    Arguements are defined at the command line via argparse

    utils.convert_ND2  : workhorse for this script. Currently defaults to processing all frames

    """
    # initialize argparser

    parser = argparse.ArgumentParser(description='Get a column from a file')

    parser.add_argument('--file',
                        dest='file_in',
                        type=str,
                        required=True,
                        help="File to be converted")

    args = parser.parse_args()

    # convert file
    file_in = args.file_in
    file_out = file_in[:-4] + '.tif'

    utils.convert_ND2(file_in, file_out)

    print('Complete!')

if __name__ == '__main__':

    main()
