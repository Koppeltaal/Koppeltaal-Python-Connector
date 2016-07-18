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


class InvalidBundle(InvalidResponse):
    pass


class InvalidValue(ValueError):

    def __init__(self, field, value=None):
        self.field = field
        self.value = value

    def __str__(self):
        return "{}: invalid value for '{}'.".format(
            self.__class__.__name__,
            self.field.name)


class InvalidCode(InvalidValue):

    def __str__(self):
        return "{}: '{}' not in '{}'.".format(
            self.__class__.__name__,
            self.value,
            self.field.system)


class InvalidResource(InvalidValue):

    def __str__(self):
        if self.field is not None:
            return "{}: expected '{}' resource type.".format(
                self.__class__.__name__,
                self.field.__class__.__name__)
        return "{}: unknown resource type.".format(
            self.__class__.__name__)


class RequiredMissing(InvalidValue):

    def __str__(self):
        return "{}: '{}' required but missing.".format(
            self.__class__.__name__,
            self.field.name)


class IFHIRResource(zope.interface.Interface):
    """A resource that can be sent to the koppeltaal server.
    """

    fhir_link = zope.interface.Attribute(
        'Link to resource containing resource type, id and version')


class IBrokenFHIRResource(IFHIRResource):
    """A resource that was broken.
    """

    error = zope.interface.Attribute(
        'Error')

    payload = zope.interface.Attribute(
        'Resource payload')


class IReferredFHIRResource(IFHIRResource):
    """A resource that is referred but missing from the resource payload
    or bundle.
    """

    display = zope.interface.Attribute(
        'Display value for this resource.')


class IIdentifiedFHIRResource(IFHIRResource):
    """A resource that can be identified with a self link.
    """


class IFHIRConfiguration(zope.interface.Interface):

    name = zope.interface.Attribute('application name using the connector')

    url = zope.interface.Attribute('fhir base URL for generated resources')

    def transaction_hook(commit_function, message):
        """Optional hook to integrate sending back a message into a
        transaction system.
        """

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

    def launch(activity, patient, user, resource=None):
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
