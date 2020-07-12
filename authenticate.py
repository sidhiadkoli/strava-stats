import logging
import json
import urllib.parse as up
import time

import requests


class Auth:
    """Manages user authentication and access tokens."""
    config_fn = '.config.json'

    def __init__(self):
        """Get access tokens and start thread to manage expiration."""
        self._load_client_config()

        if not hasattr(self, '_access_token'):
            self._authenticate()

    def _read_config(self):
        with open(Auth.config_fn) as fin:
            config = json.load(fin)
        return config

    def _write_config(self, config):
        with open(Auth.config_fn, 'w') as fin:
            json.dump(config, fin)

    def _load_client_config(self):
        """Get client id and secret from config file."""
        try:
            config = self._read_config()
            self._client_id = config['client_id']
            self._client_secret = config['client_secret']
            self._access_token = config['access_token']
            self._refresh_token = config['refresh_token']
            self._expiration = config['expires_at']
        except Exception:
            self._client_id = input("Enter client id: ")
            self._client_secret = input("Enter client secret: ")
            self._write_config({'client_id': self._client_id,
                                'client_secret': self._client_secret})

    def _authenticate(self):
        """Get access to user's activities."""
        # For now, the user needs to authenticate this script through a manual copy-pasting of URLs.
        print('Visit the following URL to authenticate: '
              f"www.strava.com/oauth/authorize?client_id={self._client_id}"
              '&redirect_uri=http://localhost&response_type=code&scope=activity:read_all')
        response_url = input('Enter the URL you were redirected to: ')
        o = up.urlparse(response_url)
        query = up.parse_qs(o.query)
        self._code = query['code']

        # Get refresh and access tokens.
        exchange_query = {'client_id': self._client_id,
                          'client_secret': self._client_secret,
                          'code': self._code,
                          'grant_type': 'authorization_code'}

        self._post_and_store_tokens('https://www.strava.com/api/v3/oauth/token', exchange_query)

    def _handle_expiration(self):
        """Update the access token and refresh token when they expire."""
        exp_query = {'client_id': self._client_id,
                     'client_secret': self._client_secret,
                     'grant_type': 'refresh_token',
                     'refresh_token': self._refresh_token}
        self._post_and_store_tokens('https://www.strava.com/api/v3/oauth/token', exp_query)

    def _post_and_store_tokens(self, url, query):
        """Post the request and store the tokens received in the response."""
        resp = requests.post(url, data=query)

        if not resp.ok:
            logging.error("Unable to get tokens. %s", resp)
            resp.raise_for_status()

        tokens = resp.json()
        self._access_token = tokens['access_token']
        self._refresh_token = tokens['refresh_token']
        self._expiration = float(tokens['expires_at'])

        config = self._read_config()
        config['access_token'] = self._access_token
        config['refresh_token'] = self._refresh_token
        config['expires_at'] = self._expiration
        self._write_config(config)

    @property
    def access_token(self):
        """Get access token. Refresh it if it has expired."""
        if time.time() > self._expiration:
            try:
                self._handle_expiration()
            except Exception:
                # Reauthenticating.
                self._authenticate()

        return self._access_token
