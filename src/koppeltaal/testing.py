import json
import pkg_resources
import urllib
import urlparse


class MockTransport(object):

    def __init__(self, module_name):
        self._module_name = module_name
        self.expected = {}
        self.called = {}

    def expect_json(self, url, fixture_names):
        if not isinstance(fixture_names, list):
            fixture_names = [fixture_names]
        self.expected[url] = [
            json.load(pkg_resources.resource_stream(self._module_name, name))
            for name in fixture_names]

    def expect_url(self, url, locations):
        if not isinstance(locations, list):
            locations = [locations]
        self.expected[url] = locations

    def relative_url(self, url, params=None):
        parts = urlparse.urlparse(url)[2:]
        url = urlparse.urlunparse(('', '') + parts)
        if params:
            url += '?' + urllib.urlencode(params)
        return url

    def query(self, url, params=None):
        url = self.relative_url(url, params)
        if not len(self.expected.get(url, [])):
            raise AssertionError('Unexpected url call')
        return self.expected[url].pop(0)

    def query_redirect(self, url, params=None):
        url = self.relative_url(url, params)
        if not len(self.expected.get(url, [])):
            raise AssertionError('Unexpected url call')
        return self.expected[url].pop(0)

    def create(self, url, data):
        url = self.relative_url(url)
        self.called[url] = data
        if not len(self.expected.get(url, [])):
            raise AssertionError('Unexpected url call')
        return self.expected[url].pop(0)

    def update(self, url, data):
        url = self.relative_url(url)
        self.called[url] = data
        if not len(self.expected.get(url, [])):
            raise AssertionError('Unexpected url call')
        return self.expected[url].pop(0)
