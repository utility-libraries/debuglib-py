# -*- coding=utf-8 -*-
r"""

"""
import argparse as ap
import sys
from . import __description__, __version__
from .defaults import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT


parser = ap.ArgumentParser(
    prog='debuglib',
    description=__description__,
    formatter_class=ap.ArgumentDefaultsHelpFormatter
)
parser.add_argument('-v', '--version', action='version', version=__version__)
parser.set_defaults(fn=parser.print_help)
subparser = parser.add_subparsers()


def cmd_listen(host: str = None, port: int = None):
    from ._cli import CLIListener
    listener = CLIListener((host, port))
    listener.run()


listen_parser = subparser.add_parser(name="listen", formatter_class=ap.ArgumentDefaultsHelpFormatter)
listen_parser.set_defaults(fn=cmd_listen)
listen_parser.add_argument('--host', type=str, default=DEFAULT_SERVER_HOST,
                           help='host to bind to')
listen_parser.add_argument('--port', type=int, default=DEFAULT_SERVER_PORT,
                           help="port to listen on")


def main():
    args = vars(parser.parse_args())
    fn = args.pop('fn')
    return fn(**args) or 0


if __name__ == '__main__':
    sys.exit(main())
