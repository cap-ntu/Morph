import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input video file', required=True)
    parser.add_argument('-s', '--resolution', nargs='*', help='resolutions of the output video file', required=True)
    #parser.add_argument('-o', '--output', help='output video file', required=True)
    args = parser.parse_args()
    print args.input
    print args.resolution
    #print args.output

