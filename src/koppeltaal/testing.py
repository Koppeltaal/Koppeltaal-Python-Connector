from hamcrest.core.base_matcher import BaseMatcher
import hamcrest
import json
import functools
import pkg_resources
import urllib
import urlparse


class MockTransport(object):

    def __init__(self, module_name):
        self._module_name = module_name
        self.clear()

    def _expect_json(self, args, url, data=None):
        return json.load(pkg_resources.resource_stream(
            self._module_name, args['json']))

    def _expect_redirect(self, args, url, data=None):
        return args['redirect']

    def clear(self):
        self.expected = {}
        self.called = {}

    def expect(self, url, **fixture):
        expect_method = None
        if 'json' in fixture:
            expect_method = functools.partial(self._expect_json, fixture)
        elif 'redirect' in fixture:
            expect_method = functools.partial(self._expect_redirect, fixture)
        assert expect_method is not None
        self.expected.setdefault(url, []).append(expect_method)

    def relative_url(self, url, params=None):
        parts = urlparse.urlparse(url)[2:]
        url = urlparse.urlunparse(('', '') + parts)
        if params:
            url += '?' + urllib.urlencode(params)
        return url

    def query(self, url, params=None):
        url = self.relative_url(url, params)
        if not len(self.expected.get(url, [])):
            raise AssertionError('Unexpected url call', url)
        expect_method = self.expected[url].pop(0)
        return expect_method(url, None)

    def query_redirect(self, url, params=None):
        url = self.relative_url(url, params)
        if not len(self.expected.get(url, [])):
            raise AssertionError('Unexpected url call', url)
        expect_method = self.expected[url].pop(0)
        return expect_method(url, None)

    def create(self, url, data):
        url = self.relative_url(url)
        self.called[url] = data
        if not len(self.expected.get(url, [])):
            raise AssertionError('Unexpected url call', url)
        expect_method = self.expected[url].pop(0)
        return expect_method(url, None)

    def update(self, url, data):
        url = self.relative_url(url)
        self.called[url] = data
        if not len(self.expected.get(url, [])):
            raise AssertionError('Unexpected url call', url)
        expect_method = self.expected[url].pop(0)
        return expect_method(url, None)


class HasFHIRExtension(BaseMatcher):

    def __init__(self, url, containing=None):
        self.url = url
        self.containing = containing
        if containing is not None:
            self.matcher = hamcrest.has_entry(
                'extension',
                hamcrest.has_item(
                    hamcrest.all_of(
                        hamcrest.has_entry(
                            'url', hamcrest.ends_with(self.url)),
                        self.containing)))
        else:
            self.matcher = hamcrest.has_entry(
                'extension',
                hamcrest.has_item(
                    hamcrest.has_entry(
                        'url', hamcrest.ends_with(self.url))))

    def _matches(self, json):
        return self.matcher.matches(json)

    def describe_to(self, description):
        description.append_text(
            'a FHIR extension ending with {} '.format(self.url))
        if self.containing is not None:
            description.append_text('containing ')
            self.containing.describe_to(description)


has_extension = HasFHIRExtension
