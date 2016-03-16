"""
Connect to Koppeltaal server
"""
import urlparse
import lxml.etree
import requests
import zope.interface
import koppeltaal
import koppeltaal.interfaces
import koppeltaal.logger
import koppeltaal.feed
import koppeltaal.metadata


@zope.interface.implementer(koppeltaal.interfaces.IConnector)
class Connector(object):
    server = None
    username = None
    password = None
    domain = None  # The domain on the server to work against.

    def __init__(self, server, username, password, domain=None):
        self.server = server
        self.username = username
        self.password = password
        self.domain = domain

    # Some nice cache decorator here.
    def metadata(self):
        # XXX Add caching based on the 'reliableCache' information.
        url = '{}/{}'.format(self.server, koppeltaal.interfaces.METADATA_URL)
        response = requests.get(
            url,
            headers={'accept': 'application/xml'},
            allow_redirects=False)
        response.raise_for_status()
        # The result is raw XML conformance statement.
        return response.content

    def test_authentication(self):
        # Perhaps some other URL to test authentication?
        url = '{}/{}'.format(
            self.server, koppeltaal.interfaces.ACTIVITY_DEFINITION_URL)
        koppeltaal.logger.debug('test_authentication %s', url)
        response = requests.get(
            url,
            headers={'accept': 'application/xml'},
            auth=(self.username, self.password),
            allow_redirects=False)
        return response.status_code == 200

    def activity_definition(self):
        url = '{}/{}'.format(
            self.server, koppeltaal.interfaces.ACTIVITY_DEFINITION_URL)
        response = requests.get(
            url,
            auth=(self.username, self.password),
            headers={'Accept': 'application/xml'},
            allow_redirects=False)
        response.raise_for_status()

        koppeltaal.logger.debug(
            'Activity definition response {}'.format(response.content))

        return response.content

    def post_message(self, xml):
        # XXX seems only used for creating care plans so far.

        # Get from the metadata definition
        mailbox_url = koppeltaal.metadata.metadata(
            self.metadata())['messaging']['endpoint']

        # Assert that the protocol is the same.
        assert urlparse.urlparse(mailbox_url).scheme == urlparse.urlparse(
            self.server).scheme

        koppeltaal.logger.debug('Post message {}'.format(xml))

        response = requests.post(
            mailbox_url,
            auth=(self.username, self.password),
            data=xml,
            headers={
                'Accept': 'application/xml',
                'Content-Type': 'application/xml',
            },
            allow_redirects=False)
        response.raise_for_status()

        koppeltaal.logger.debug(
            'Post message response {}'.format(response.content))

        return response.content

    def launch(self, activity, patient, user):
        response = requests.get(
            '{}/{}'.format(
                self.server, koppeltaal.interfaces.OAUTH_LAUNCH_URL),
            auth=(self.username, self.password),
            params={
                'client_id': activity.identifier,  # XXX weird...
                'patient': koppeltaal.url(patient),
                'user': koppeltaal.url(user),
                'resource': activity.identifier  # XXX Not to sure about this.
            },
            allow_redirects=False)
        assert response.is_redirect
        # The Launch sequence returns a redirect to the URL we should present
        # to the user.
        return response.headers.get('location')

    def _do_message_query(self, params):
        url = '{}/{}/_search'.format(
            self.server, koppeltaal.interfaces.MESSAGE_HEADER_URL)
        response = requests.get(
            url,
            params=params,
            auth=(self.username, self.password),
            headers={'Accept': 'application/xml'},
            allow_redirects=False)
        response.raise_for_status()
        return response.content

    def messages(
            self,
            patient=None,
            processing_status=None,
            summary=False,
            count=5000):
        # NOTE this barebones implementation is intened to be replaced by
        # higher-level models in message.py (and other modules).
        params = {'_count': count}
        if patient:
            params['Patient'] = koppeltaal.url(patient)
        if processing_status:
            params['ProcessingStatus'] = processing_status
        if summary:
            params['_summary'] = 'true'
        return self._do_message_query(params)

    def message(self, id):
        # NOTE this barebones implementation is intened to be replaced by
        # higher-level models in message.py (and other modules).
        return self._do_message_query({'_id': id})

    def _process_message(self, id, action):
        # NOTE this barebones implementation is intened to be replaced by
        # higher-level models in message.py (and other modules).
        if action not in koppeltaal.interfaces.PROCESSING_ACTIONS:
            raise ValueError('Action {} unkown'.format(action))
        message_header = (
            resource for resource in koppeltaal.feed.parse(self.message(id))
            if isinstance(resource, koppeltaal.model.MessageHeader)).next()
        # Set the status and set the new processing status.
        message_header.status = action
        response = requests.put(
            message_header.__version__,
            data=lxml.etree.tostring(message_header.__node__),
            auth=(self.username, self.password),
            headers={'Accept': 'application/xml'},
            allow_redirects=False)
        response.raise_for_status()
        return response.content

    def claim(self, id):
        # NOTE this barebones implementation is intened to be replaced by
        # higher-level models in message.py (and other modules).
        return self._process_message(
            id, koppeltaal.interfaces.PROCESSING_STATUS_CLAIMED)

    def success(self, id):
        # NOTE this barebones implementation is intened to be replaced by
        # higher-level models in message.py (and other modules).
        return self._process_message(
            id, koppeltaal.interfaces.PROCESSING_STATUS_SUCCESS)

    def fail(self, id):
        # NOTE this barebones implementation is intened to be replaced by
        # higher-level models in message.py (and other modules).
        return self._process_message(
            id, koppeltaal.interfaces.PROCESSING_STATUS_FAILED)
