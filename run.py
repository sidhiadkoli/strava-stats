#!/usr/bin/env python3

import argparse
import logging
import sys

from stats import Stats


def main():
    """Loop to handle user's stats queries."""
    ss = Stats()

    stats_query = input('Enter query: ')

    while stats_query != 'exit':
        ss.resolve_query(stats_query)

        # Get next query.
        stats_query = input('Enter query: ')


def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='WARNING')
    return parser.parse_args(args)


def setup_logging(loglevel):
    logging.basicConfig(format='%(message)s', level=getattr(logging, loglevel, None))


if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])
    setup_logging(args.loglevel)

    main()
