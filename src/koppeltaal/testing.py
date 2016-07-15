import json
import pkg_resources
import urllib
import urlparse


class MockTransport(object):

    def __init__(self, module_name):
        self._module_name = module_name
        self.expected = {}
        self.called = {}

    def expect_json(self, url, fixture_name):
        self.expected[url] = json.load(
            pkg_resources.resource_stream(self._module_name, fixture_name))

    def expect_url(self, url, location):
        self.expected[url] = location

    def relative_url(self, url, params=None):
        parts = urlparse.urlparse(url)[2:]
        url = urlparse.urlunparse(('', '') + parts)
        if params:
            url += '?' + urllib.urlencode(params)
        return url

    def query(self, url, params=None):
        url = self.relative_url(url, params)
        if url not in self.expected:
            raise AssertionError('Unexpected url call')
        return self.expected[url]

    def query_redirect(self, url, params=None):
        url = self.relative_url(url, params)
        if url not in self.expected:
            raise AssertionError('Unexpected url call')
        return self.expected[url]

    def create(self, url, data):
        url = self.relative_url(url)
        self.called[url] = data
        if url not in self.expected:
            raise AssertionError('Unexpected url call')
        return self.expected[url]

    def update(self, url, data):
        url = self.relative_url(url)
        self.called[url] = data
        if url not in self.expected:
            raise AssertionError('Unexpected url call')
        return self.expected[url]
