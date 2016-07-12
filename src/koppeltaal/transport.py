import urlparse
import requests

from koppeltaal import (interfaces, logger)


class Transport(object):

    def __init__(self, server, username, password):
        parts = urlparse.urlparse(server)

        self.scheme = parts.scheme
        self.netloc = parts.netloc
        self.username = username
        self.password = password

        self.session = requests.Session()

    def absolute_url(self, url):
        # Make sure we talk to the proper server by updating the URL.
        parts = urlparse.urlparse(url)[2:]
        return urlparse.urlunparse((self.scheme, self.netloc) + parts)

    def query(self, url, params=None):
        """Query a url.
        """
        response = self.session.get(
            self.absolute_url(url),
            params=params,
            auth=(self.username, self.password),
            headers={'Accept': 'application/json'},
            allow_redirects=False)
        response.raise_for_status()
        if not response.headers['content-type'].startswith('application/json'):
            raise interfaces.InvalidResponse(response.text)
        json = response.json()
        logger.debug_json('Query on {url}:\n {json}', json=json, url=url)
        return json

    def query_redirect(self, url, params=None):
        """Query a url for a redirect.
        """
        response = self.session.get(
            self.absolute_url(url),
            params=params,
            auth=(self.username, self.password),
            allow_redirects=False)
        if not response.is_redirect:
            raise interfaces.InvalidResponse()
        return response.headers.get('location')

    def create(self, url, data):
        """Create a new resource at the given url with JSON data.
        """
        response = self.session.post(
            self.absolute_url(url),
            auth=(self.username, self.password),
            json=data,
            headers={'Accept': 'application/json'},
            allow_redirects=False)
        response.raise_for_status()
        if not response.headers['content-type'].startswith('application/json'):
            raise interfaces.InvalidResponse(response.text)
        if response.text:
            json = response.json()
            logger.debug_json('Create on {url}:\n {json}', json=json, url=url)
            return json
        return None

    def update(self, url, data):
        """Update an existing resource at the given url with JSON data.
        """
        response = self.session.put(
            self.absolute_url(url),
            auth=(self.username, self.password),
            json=data,
            headers={'Accept': 'application/json'},
            allow_redirects=False)
        response.raise_for_status()
        if not response.headers['content-type'].startswith('application/json'):
            raise interfaces.InvalidResponse(response.text)
        if response.text:
            json = response.json()
            logger.debug_json('Update on {url}:\n {json}', json=json, url=url)
            return json
        return None
