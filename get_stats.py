import argparse
import logging
import sys


def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='WARNING')
    return parser.parse_args(args)


def setup_logging(args):
    logging.basicConfig(format='%(message)s', level=getattr(logging, args.loglevel, None))


if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])
    setup_logging(args)
