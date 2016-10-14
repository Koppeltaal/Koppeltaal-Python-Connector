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
            self._module_name, args['respond_with']))

    def _expect_redirect(self, args, url, data=None):
        return args['redirect_to']

    def clear(self):
        self.expected = {}
        self.called = {}

    def expect(self, url, **fixture):
        """Register an URL that the transport expects to be called for.

        Fixture(s) is the contents that the transport returns when the
        corresponding expected URL is called. When registering fixtures for
        the same URL multiple times, they are returned in that order.

        Note how the data that is to be sent to the expected URL is stored in
        the `called` attribute when indeed the expected URL is called.
        """
        expect_method = None
        if 'respond_with' in fixture:
            expect_method = functools.partial(self._expect_json, fixture)
        elif 'redirect_to' in fixture:
            expect_method = functools.partial(self._expect_redirect, fixture)
        assert expect_method is not None
        self.expected.setdefault(url, []).append(expect_method)

    def relative_url(self, url, params=None):
        parts = urlparse.urlparse(url)[2:]
        url = urlparse.urlunparse(('', '') + parts)
        if params:
            url += '?' + urllib.urlencode(params)
        return url

    def absolute_url(self, url):
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

    def post(self, url, data):
        url = self.relative_url(url)
        self.called[url] = data
        if not len(self.expected.get(url, [])):
            raise AssertionError('Unexpected url call', url)
        expect_method = self.expected[url].pop(0)
        return expect_method(url, None)

    create = update = post


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


class HasProcessingStatusException(BaseMatcher):

    def __init__(self, error, containing=None):
        self.error = error
        self.containing = containing
        if containing is not None:
            self.matcher = has_extension(
                '#ProcessingStatus',
                hamcrest.all_of(
                    has_extension(
                        '#ProcessingStatusStatus',
                        hamcrest.has_entry('valueCode', 'Failed')),
                    has_extension(
                        '#ProcessingStatusException',
                        hamcrest.has_entry(
                            'valueString', self.error)),
                        self.containing))
        else:
            self.matcher = has_extension(
                '#ProcessingStatus',
                hamcrest.all_of(
                    has_extension(
                        '#ProcessingStatusStatus',
                        hamcrest.has_entry('valueCode', 'Failed')),
                    has_extension(
                        '#ProcessingStatusException',
                        hamcrest.has_entry(
                            'valueString', self.error))))

    def _matches(self, json):
        return self.matcher.matches(json)

    def describe_to(self, description):
        description.append_text(
            'a valueString {} '.format(self.error))
        if self.containing is not None:
            description.append_text('containing ')
            self.containing.describe_to(description)


has_exception = HasProcessingStatusException
