import json
import pkg_resources
import urllib


class MockTransport(object):

    def __init__(self):
        self.expected = {}
        self.called = {}

    def expect_json(self, url, module_name, fixture_name):
        self.expected[url] = json.load(
            pkg_resources.resource_stream(module_name, fixture_name))

    def expect_url(self, url, location):
        self.expected[url] = location

    def query(self, url, params=None):
        if params:
            url += '?' + urllib.urlencode(params)

        if url not in self.expected:
            raise AssertionError('Unexpected url call')
        return self.expected[url]

    def query_redirect(self, url, params=None):
        if params:
            url += '?' + urllib.urlencode(params)
        if url not in self.expected:
            raise AssertionError('Unexpected url call')
        return self.expected[url]

    def create(self, url, data):
        self.called[url] = data
        if url not in self.expected:
            raise AssertionError('Unexpected url call')
        return self.expected[url]

    def update(self, url, data):
        self.called[url] = data
        if url not in self.expected:
            raise AssertionError('Unexpected url call')
        return self.expected[url]
