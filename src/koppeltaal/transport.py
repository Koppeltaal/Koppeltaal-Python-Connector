# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import requests
import six

from koppeltaal import (interfaces, logger)
from six.moves.urllib.parse import urlparse, urlunparse


unicode = six.text_type


class Response(object):

    def __init__(self, json=None, location=None):
        self.json = json
        self.location = location


class Transport(object):

    def __init__(self, server, username, password):
        parts = urlparse(server)

        self.server = server
        self.scheme = parts.scheme
        self.netloc = parts.netloc
        self.username = username
        self.password = password

        self.session = requests.Session()

    def absolute_url(self, url):
        # Make sure we talk to the proper server by updating the URL.
        parts = list(map(unicode, urlparse(url)[2:]))
        return urlunparse([unicode(self.scheme), unicode(self.netloc)] + parts)

    def _read_http_response(self, http_response):
        if not http_response.headers['content-type'].startswith(
                'application/json'):
            raise interfaces.ConnectionError(http_response)
        response = Response(
            json=http_response.json() if http_response.text else None,
            location=http_response.headers.get('content-location'))
        if 400 <= http_response.status_code < 600:
            raise interfaces.ResponseError(response)
        return response

    def query(self, url, params=None, username=None, password=None):
        """Query a url.
        """
        try:
            http_response = self.session.get(
                self.absolute_url(url),
                params=params,
                auth=(username or self.username, password or self.password),
                headers={'Accept': 'application/json'},
                timeout=interfaces.TIMEOUT,
                allow_redirects=False)
        except requests.RequestException as error:
            raise interfaces.ConnectionError(error)
        return self._read_http_response(http_response)

    def query_redirect(self, url, params=None):
        """Query a url for a redirect.
        """
        try:
            http_response = self.session.get(
                self.absolute_url(url),
                params=params,
                auth=(self.username, self.password),
                timeout=interfaces.TIMEOUT,
                allow_redirects=False)
        except requests.RequestException as error:
            raise interfaces.ConnectionError(error)
        if not http_response.is_redirect:
            raise interfaces.ConnectionError(http_response)
        return Response(location=http_response.headers.get('location'))

    def create(self, url, data):
        """Create a new resource at the given url with JSON data.
        """
        try:
            http_response = self.session.post(
                self.absolute_url(url),
                auth=(self.username, self.password),
                json=data,
                headers={'Accept': 'application/json'},
                timeout=interfaces.TIMEOUT,
                allow_redirects=False)
        except requests.RequestException as error:
            raise interfaces.ConnectionError(error)
        return self._read_http_response(http_response)

    def update(self, url, data):
        """Update an existing resource at the given url with JSON data.
        """
        try:
            http_response = self.session.put(
                self.absolute_url(url),
                auth=(self.username, self.password),
                json=data,
                headers={'Accept': 'application/json'},
                timeout=interfaces.TIMEOUT,
                allow_redirects=False)
        except requests.RequestException as error:
            raise interfaces.ConnectionError(error)
        return self._read_http_response(http_response)

    def close(self):
        self.session.close()
