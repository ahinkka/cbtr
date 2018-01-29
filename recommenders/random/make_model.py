import os
from patharg import PathType


def write_model(indir, outfile):
    for item in os.listdir(indir):
        print(item.strip().replace('.txt', ''), file=outfile)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('indir', type=PathType(exists=True, type='dir'))
    parser.add_argument('outfile', type=argparse.FileType('w'))
    args = parser.parse_args()
    write_model(args.indir, args.outfile)
