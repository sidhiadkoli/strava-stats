import logging
import json
import urllib.parse as up
import time

import requests


class Auth:
    """Manages user authentication and access tokens."""
    def __init__(self):
        """Get access tokens and start thread to manage expiration."""
        self._load_client_config()
        self._authenticate()

    def _load_client_config(self):
        """Get client id and secret from config file."""
        with open('.config.json') as fin:
            config = json.load(fin)

        self._client_id = config['id']
        self._client_secret = config['secret']

    def _authenticate(self):
        """Get access to user's activities."""
        # For now, the user needs to authenticate this script through a manual copy-pasting of URLs.
        print("Visit the following URL to authenticate: "
              f"www.strava.com/oauth/authorize?client_id={self._client_id}"
              "&redirect_uri=http://localhost&response_type=code&scope=activity:read_all")
        response_url = input("Enter the URL you were redirected to: ")
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

    def _post_and_store_token(self, url, query):
        """Post the request and store the tokens received in the response."""
        resp = requests.post(url, data=query)

        if not resp.ok():
            logging.error("Unable to get tokens. %s", resp)
            resp.raise_for_status()

        tokens = resp.json()
        self._access_token = tokens['access_token']
        self._refresh_token = tokens['refresh_token']
        self._expiration = tokens['expires_at']

    @property
    def access_token(self):
        """Get access token. Refresh it if it has expired."""
        if time.time() > self.expiration:
            self._handle_expiration()

        return self._access_token
