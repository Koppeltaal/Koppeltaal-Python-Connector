"""
Connect to Koppeltaal server
"""
import requests
import koppeltaal
import koppeltaal.metadata

# The URLs that can't be reached from the metadata are defined as constants
# here.
METADATA_URL = 'FHIR/Koppeltaal/metadata'
ACTIVITY_DEFINITION_URL = 'FHIR/Koppeltaal/Other?code=ActivityDefinition'


# XXX Get these from the metadata / Conformance statement.
# /implementation/url@value
FHIR = 'FHIR/Koppeltaal'
OAUTH_LAUNCH = 'OAuth2/Koppeltaal/Launch'

# XXX Request pool, take into account multiple apps may be using this same
# piece of code.

class Connector(object):
    server = None
    username = None
    password = None

    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password

    # Some nice cache decorator here.
    def metadata(self):
        # XXX Add caching based on the 'reliableCache' information.
        url = '{}/{}'.format(self.server, METADATA_URL)
        response = requests.get(
            url,
            headers={'accept': 'application/xml'})
        response.raise_for_status()
        # The result is raw XML conformance statement.
        return response.content

    def test_authentication(self):
        # Perhaps some other URL to test authentication?
        url = '{}/{}'.format(self.server, ACTIVITY_DEFINITION_URL)
        koppeltaal.logger.debug('test_authentication %s', url)
        response = requests.get(
            url,
            headers={'accept': 'application/xml'},
            auth=(self.username, self.password))
        return response.status_code == 200

    def activity_definition(self):
        # XXX Cache this information?
        url = '{}/{}'.format(self.server, ACTIVITY_DEFINITION_URL)
        response = requests.get(
            url,
            auth=(self.username, self.password),
            headers={'Accept': 'application/xml'})
        response.raise_for_status()
        return response.content

    def create_or_update_care_plan(self, xml):
        # Get from the metadata definition
        mailbox_url = koppeltaal.metadata.metadata(
            self.metadata())['messaging']['endpoint']
        koppeltaal.logger.debug('Sending XML %s', xml)
        response = requests.post(
            mailbox_url,
            auth=(self.username, self.password),
            data=xml,
            headers={
                'Accept': 'application/xml',
                'Content-Type': 'application/xml',
            })
        response.raise_for_status()
        # We could parse the response.
        # In the response find the URL to the newly created careplan:
        # XXX History information.
        return response.content

    def launch(self, activity_id, patient_url, user_url):
        response = requests.get(
            '{}/{}'.format(self.server, OAUTH_LAUNCH),
            auth=(self.username, self.password),
            params={
                'client_id': activity_id,
                'patient': patient_url,
                'user': user_url,
                'resource': activity_id
            })
        assert response.is_redirect
        # The Launch sequence returns a redirect to the URL we should present
        # to the user.
        return response.headers.get('location')

    # XXX Need to be reviewed first.

    def message_header(self, patient_id=None, message_id=None):
        # XXX No tests for this yet.
        """Search for the message for the patient_id or
        get the message with that specific id."""
        # XXX Split in separate search and retrieve functions.
        assert (patient_id is not None) ^ (message_id is not None)
        url = '/'.join([self.server, FHIR, 'MessageHeader'])
        if patient_id is not None:
            # messages for a specific patient resource.
            url += '/_search?_count=1000&Patient={}/FHIR/Patient/{}'.format('foo', patient_id)
            # XXX In case of more than one page, we need to do pagination.
        if message_id is not None:
            # specific message id.
            url += '/_search?_id={}'.format(message_id)
        response = requests.get(
            url,
            auth=(self.username, self.password),
            headers={'Accept': 'application/xml'})
        response.raise_for_status()
        return response.content

    def get_next_and_claim(self):
        # XXX No tests yet.
        url = '/'.join([
            self.server, FHIR,
            'MessageHeader?_query=MessageHeader.GetNextNewAndClaim'])
        response = requests.get(
            url,
            auth=(self.username, self.password),
            headers={'accept': 'application/xml'})
        response.raise_for_status()
        return response.content
