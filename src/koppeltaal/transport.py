import urlparse
import requests

from koppeltaal import interfaces


class Transport(object):

    def __init__(self, server, username, password):
        parts = urlparse.urlparse(server)

        self.scheme = parts.scheme
        self.netloc = parts.netloc
        self.username = username
        self.password = password

    def absolute_url(self, url):
        # Make sure we talk to the proper server by updating the URL.
        parts = urlparse.urlparse(url)[2:]
        return urlparse.urlunparse((self.scheme, self.netloc) + parts)

    def query(self, url, params=None):
        """Query a url.
        """
        response = requests.get(
            self.absolute_url(url),
            params=params,
            auth=(self.username, self.password),
            headers={'Accept': 'application/json'},
            allow_redirects=False)
        response.raise_for_status()
        if not response.headers['content-type'].startswith('application/json'):
            raise interfaces.InvalidResponse(response.text)
        return response.json()

    def query_redirect(self, url, params=None):
        """Query a url for a redirect.
        """
        response = requests.get(
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
        response = requests.post(
            self.absolute_url(url),
            auth=(self.username, self.password),
            json=data,
            headers={'Accept': 'application/json'},
            allow_redirects=False)
        response.raise_for_status()
        if not response.headers['content-type'].startswith('application/json'):
            raise interfaces.InvalidResponse(response.text)
        if response.text:
            return response.json()
        return None

    def update(self, url, data):
        """Update an existing resource at the given url with JSON data.
        """
        response = requests.put(
            self.absolute_url(url),
            auth=(self.username, self.password),
            json=data,
            headers={'Accept': 'application/json'},
            allow_redirects=False)
        response.raise_for_status()
        if not response.headers['content-type'].startswith('application/json'):
            raise interfaces.InvalidResponse(response.text)
        if response.text:
            return response.json()
        return None
