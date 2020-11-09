# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import pkg_resources
import zope.interface

NAMESPACE = 'http://ggz.koppeltaal.nl/fhir/Koppeltaal/'

SOFTWARE = 'Koppeltaal python adapter'
VERSION = pkg_resources.get_distribution('koppeltaal').version

OTHER_URL = '/FHIR/Koppeltaal/Other'
ACTIVITY_DEFINITION_URL = '/FHIR/Koppeltaal/Other/_search'
MESSAGE_HEADER_URL = '/FHIR/Koppeltaal/MessageHeader/_search'
METADATA_URL = '/FHIR/Koppeltaal/metadata'
MAILBOX_URL = '/FHIR/Koppeltaal/Mailbox'
OAUTH_AUTHORIZE_URL = 'OAuth2/Koppeltaal/Authorize'
OAUTH_LAUNCH_URL = '/OAuth2/Koppeltaal/Launch'
OAUTH_TOKEN_URL = '/OAuth2/Koppeltaal/Token'

TIMEOUT = 60


class KoppeltaalError(ValueError):
    """Generic koppeltaal error.
    """


class TransportError(KoppeltaalError):
    """There was an error related to the transport.
    """


class ConnectionError(TransportError):
    """There was a connection error from the transport.
    """


class ResponseError(TransportError):
    """The transport got a response but it was an error.
    """

    def __init__(self, response):
        super(ResponseError, self).__init__(response)
        self.response = response

    def __str__(self):
        return "{}: {}.".format(self.__class__.__name__, self.response.__dict__)


class OperationOutcomeError(KoppeltaalError):
    """A non 200 status with an operation outcome was returned by the server.
    """

    def __init__(self, outcome):
        super(OperationOutcomeError, self).__init__(outcome)
        self.outcome = outcome

    def __str__(self):
        issues = []
        for issue in self.outcome.issue:
            issues.append('type: {}, resource: {}, details: {}'.format(
                issue.type,
                issue.resource and issue.resource.fhir_link,
                issue.details))
        return "{}: outcome issue(s): {}.".format(
            self.__class__.__name__, issues)


class MessageResponseError(KoppeltaalError):
    """The response in the message header reported an error.
    """

    def __init__(self, message):
        super(MessageResponseError, self).__init__(message)
        self.message = message

    def __str__(self):
        return "{}: {}.".format(self.__class__.__name__, str(self.message))


class DummyError(KoppeltaalError):
    """Error generated when you ask the dummy connector to perform an action.
    """

    def __str__(self):
        return "{}: connector in dummy mode.".format(
            self.__class__.__name__)


class InvalidBundle(KoppeltaalError):
    """A malformed bundle was obtain from the koppeltaal server.
    """


class InvalidValue(KoppeltaalError):
    """A value does not match the definition for its corresponding field
    in the koppeltaal definitions.
    """

    def __init__(self, field, value=None):
        self.field = field
        self.value = value

    def __str__(self):
        python_name = self.field.getName()
        extended = python_name != self.field.name
        if self.field.interface is not None:
            python_name = self.field.interface.getName() + '.' + python_name
        if extended:
            return "{}: invalid value '{}' for '{}' (FHIR name: '{}').".format(
                self.__class__.__name__, self.value,
                python_name, self.field.name)
        return "{}: invalid value '{}' for '{}'.".format(
            self.__class__.__name__, self.value, python_name)


class InvalidReference(InvalidValue):
    """A value that is not a valid reference.
    """

    field = None

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "invalid reference '{}'.".format(
            self.value.__class__.__name__)


class InvalidCode(InvalidValue):
    """A code appear that is not expected in its definition.
    """

    def __str__(self):
        if self.value:
            return "{}: '{}' not in '{}'.".format(
                self.__class__.__name__,
                self.value,
                self.field.system)
        return "{}: code is missing.".format(self.__class__.__name__)


class InvalidSystem(InvalidCode):
    """The system mentioned by the code is not allowed/supported here.
    """

    def __str__(self):
        if self.value:
            return "{}: system '{}' is not supported.".format(
                self.__class__.__name__,
                self.value)
        return "{}: system is missing.".format(self.__class__.__name__)


class InvalidResource(InvalidValue):
    """A resource type mismatch expected in the koppeltaal definitions.
    """

    def __str__(self):
        if self.field is not None:
            return "{}: expected '{}' resource type.".format(
                self.__class__.__name__,
                self.field.__class__.__name__)
        return "{}: unknown resource type.".format(
            self.__class__.__name__)


class RequiredMissing(InvalidValue):
    """A field is required in the koppeltaal definitions but its value is
    missing.
    """

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


class IIntegration(zope.interface.Interface):
    """Personalizing of connector settings and behavior.
    """

    name = zope.interface.Attribute('application name using the connector')

    url = zope.interface.Attribute('fhir base URL for generated resources')

    client_id = zope.interface.Attribute(
        'Application identifier for the domain')

    client_secret = zope.interface.Attribute(
        'OAUTH secret for this application client')

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


class IUpdate(zope.interface.Interface):
    """Update retrieved from a message via the connector. It can be used a
    context manager to automatically update the processing status of
    the message.
    """
    message = zope.interface.Attribute('message related to the update')

    data = zope.interface.Attribute('focal resource of the message')

    patient = zope.interface.Attribute('patient related to the message')

    def success():
        """Mark the message as succeed.
        """

    def fail(exception="FAILED"):
        """Mark the message as failed, with the given exception message.
        """

    def postpone():
        """Do nothing. The message will stay in claim an eventually revert
        back to new.
        """


class IConnector(zope.interface.Interface):
    """Connector to interact with the koppeltaal server.
    """

    transport = zope.interface.Attribute('transport to access the server')

    domain = zope.interface.Attribute('domain')

    integration = zope.interface.Attribute('integration for this connector')

    def metadata():
        """Return the conformance statement.
        """

    def activities(archived=False):
        """Return a list of activity definitions.
        """

    def activity(identifier, archived=False):
        """Return a specific activity definition identified by `identifier` or
        None.
        """

    def launch(careplan, user=None, activity_identifier=None):
        """Retrieve launch URL for an activity in a careplan for a give user..
        """

    def launch_from_parameters(
            application_id, patient_link, user_link, activity_identifier):
        """Retrieve launch URL out of all required parameters. Those
        parameters can be extracted from a careplan.
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

    def close():
        """Close any connection left to the server.
        """
