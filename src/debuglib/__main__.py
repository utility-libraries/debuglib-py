# -*- coding=utf-8 -*-
r"""

"""
import argparse as ap
import sys
from . import __description__, __version__


parser = ap.ArgumentParser(prog='debuglib', description=__description__)
parser.add_argument('-v', '--version', action='version', version=__version__)


def main():
    parser.parse_args()
    print("Currently under development")
    return 0


if __name__ == '__main__':
    sys.exit(main())
