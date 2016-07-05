import urlparse
import requests
import zope.interface
import koppeltaal.interfaces
import koppeltaal.bundle
import koppeltaal.utils

DEFAULT_COUNT = 100


class InvalidResponse(ValueError):
    pass


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
            raise InvalidResponse(response.text)
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
            raise InvalidResponse()
        return response.headers.get('location')

    def query_bundle(self, url, params=None):
        """Query a URL, and expect one or more resources packaged as a bundle
        from it.
        """
        next_url = url
        next_params = params
        bundle = koppeltaal.bundle.Bundle()
        while next_url:
            response = self.query(next_url, next_params)
            bundle.add_response(response)
            next_url = koppeltaal.utils.json2links(response).get('next')
            next_params = None  # Parameters are already in the next link.
        return bundle.unpack()

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
            raise InvalidResponse(response.text)
        return response.json()

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
            raise InvalidResponse(response.text)
        return response.json()


@zope.interface.implementer(koppeltaal.interfaces.IConnector)
class Connector(object):

    def __init__(self, server, username, password, domain=None):
        self.transport = Transport(server, username, password)
        self.domain = domain

    def metadata(self):
        return self.transport.query(
            koppeltaal.interfaces.METADATA_URL)

    def activities(self):
        return self.transport.query_bundle(
            koppeltaal.interfaces.ACTIVITY_DEFINITION_URL,
            {'code': 'ActivityDefinition'})

    def activity(self, identifier):
        for activity in self.activities():
            if activity.identifier == identifier:
                return activity
        return None

    def launch(self, activity, patient, user):
        params = {
            'client_id': activity.identifier,
            'patient': patient.uid,
            'user': user.uid,
            'resource': activity.identifier}
        return self.transport.query_redirect(
            koppeltaal.interfaces.OAUTH_LAUNCH_URL,
            params)

    def fetch(
            self, message_id=None, event=None, status=None, patient=None):
        params = {}
        if message_id:
            params['_id'] = message_id
        else:
            params['_summary'] = 'true'
            params['_count'] = DEFAULT_COUNT
        if event:
            params['event'] = event
        if status:
            params['ProcessingStatus'] = status
        if patient:
            params['Patient'] = patient
        return self.transport.query_bundle(
            koppeltaal.interfaces.MESSAGE_HEADER_URL, params)

    def send(self, message):
        # feed.category(
        #     term='{koppeltaal}/Domain#{domain}'.format(
        #         domain=domain, **koppeltaal.NS),
        #     label=domain,
        #     scheme='{fhir}/tag/security'.format(**koppeltaal.NS))
        # feed.category(
        #     term='{fhir}/tag/message'.format(**koppeltaal.NS),
        #     scheme='{fhir}/tag'.format(**koppeltaal.NS))

        # self.transport.update(message.uid_with_history, serialize(message))
        pass
