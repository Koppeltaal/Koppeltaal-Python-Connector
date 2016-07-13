import pkg_resources
import zope.interface

NAMESPACE = 'http://ggz.koppeltaal.nl/fhir/Koppeltaal/'

SOFTWARE = 'Koppeltaal python adapter'
VERSION = pkg_resources.get_distribution('koppeltaal').version

ACTIVITY_DEFINITION_URL = '/FHIR/Koppeltaal/Other/_search'
MESSAGE_HEADER_URL = '/FHIR/Koppeltaal/MessageHeader/_search'
METADATA_URL = '/FHIR/Koppeltaal/metadata'
MAILBOX_URL = '/FHIR/Koppeltaal/Mailbox'
OAUTH_LAUNCH_URL = '/OAuth2/Koppeltaal/Launch'


class InvalidResponse(ValueError):
    pass


class InvalidBundle(ValueError):
    pass


class InvalidValue(ValueError):

    def __init__(self, field, value=None):
        self.field = field
        self.value = value


class RequiredMissing(InvalidValue):
    pass


class IFHIRResource(zope.interface.Interface):
    """A resource that can be sent to the koppeltaal server.
    """

    fhir_link = zope.interface.Attribute(
        'Link to resource containing resource type, id and version')


class IIdentifiedFHIRResource(IFHIRResource):
    """A resource that can be identified.
    """


class IFHIRConfiguration(zope.interface.Interface):

    name = zope.interface.Attribute('application name using the connector')

    url = zope.interface.Attribute('fhir base URL for generated resources')

    def model_id(model):
        """Return a (unique) id for the given `model`. Should stay the same id
        if called again with the same model.
        """

    def link(model, resource_type):
        """Return fhir URL for `model` which is a `resource_type`.
        """


class IConnector(zope.interface.Interface):
    """Connector to interact with the koppeltaal server.
    """

    transport = zope.interface.Attribute('transport to access the server')

    domain = zope.interface.Attribute('domain')

    configuration = zope.interface.Attribute('fhir configuration')

    def metadata():
        """Return the conformance statement.
        """

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

    def updates():
        """Iterate over the available new messages in the mailbox for
        processing.
        """

    def search(message_id=None, event=None, status=None, patient=None):
        """Return a list of messages matching the given criteria.
        """

    def send(event, data, patient):
        """Send an update about event with data for patient.
        """
