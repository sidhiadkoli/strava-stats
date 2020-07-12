#!/usr/bin/env python3

import argparse
import logging
import sys

from stats import Stats


def main():
    """Loop to handle user's stats queries."""
    ss = Stats()

    stats_query = input('Enter query: ').lower()

    while stats_query != 'exit':
        try:
            ss.resolve_query(stats_query)
        except Exception:
            logging.exception('Unable to execute query.')

        # Get next query.
        stats_query = input('Enter query: ').lower()


def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='WARNING')
    return parser.parse_args(args)


def setup_logging(loglevel):
    logging.basicConfig(format='%(levelname)s: %(message)s', level=getattr(logging, loglevel, None))


if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])
    setup_logging(args.loglevel)

    main()
