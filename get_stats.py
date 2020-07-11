#!/usr/bin/env python3

import argparse
import json
import logging
import sys
import urllib.parse as up

import requests


def authenticate():
    """Get access to user's activities."""
    # For now, the user needs to authenticate this script through a manual copy-pasting of URLs.
    with open('.config.json') as fin:
        config = json.load(fin)

    print("Visit the following URL to authenticate: "
          f"www.strava.com/oauth/authorize?client_id={config['id']}"
          "&redirect_uri=http://localhost&response_type=code&scope=activity:read_all")
    response_url = input("Enter the URL you were redirected to: ")
    o = up.urlparse(response_url)
    query = up.parse_qs(o.query)
    code = query['code']

    # Get refresh and access tokens.
    exchange_query = {'client_id': config['id'],
                      'client_secret': config['secret'],
                      'code': code,
                      'grant_type': 'authorization_code'}
    resp = requests.post('https://www.strava.com/api/v3/oauth/token', data=exchange_query)
    resp.raise_for_status()
    tokens = resp.json()
    logging.info("Successfully authenticated %s!", tokens['athlete']['firstname'])
    return tokens['access_token'], tokens['refresh_token'], tokens['expires_at']


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

    access_token, refresh_token, _ = authenticate()
