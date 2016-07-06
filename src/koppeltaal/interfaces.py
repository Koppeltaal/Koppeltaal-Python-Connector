import zope.interface

NAMESPACE = 'http://ggz.koppeltaal.nl/fhir/Koppeltaal/'

ACTIVITY_DEFINITION_URL = '/FHIR/Koppeltaal/Other/_search'
MESSAGE_HEADER_URL = '/FHIR/Koppeltaal/MessageHeader/_search'
METADATA_URL = '/FHIR/Koppeltaal/metadata'
OAUTH_LAUNCH_URL = '/OAuth2/Koppeltaal/Launch'


class InvalidBundle(ValueError):
    pass


class InvalidValue(ValueError):

    def __init__(self, field, value=None):
        self.field = field
        self.value = value


class RequiredMissing(InvalidValue):
    pass


class IConnector(zope.interface.Interface):

    transport = zope.interface.Attribute('server base URL')

    domain = zope.interface.Attribute('domain')

    def metadata():
        pass

    def activities():
        """Return a list of activity definitions.
        """

    def activity(identifier):
        """Return a specific activity definition identified by `identifier` or
        None.
        """

    def launch(activity, patient, user):
        """Retrieve launch URL for a specific `activity` which have been added
        to a `patient` to be used by `user`.
        """

    def fetch(message_id=None, event=None, status=None, patient=None):
        """Return a list of messages matching the given criteria.
        """

    def send(message):
        """Send a message.
        """
