import zope.interface

NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'fhir': 'http://hl7.org/fhir',
    'koppeltaal': 'http://ggz.koppeltaal.nl/fhir/Koppeltaal',
    }


PROCESSING_STATUS_CLAIMED = 'Claimed'
PROCESSING_STATUS_FAILED = 'Failed'
PROCESSING_STATUS_NEW = 'New'
PROCESSING_STATUS_SUCCESS = 'Success'


PROCESSING_ACTIONS = (
    PROCESSING_STATUS_CLAIMED,
    PROCESSING_STATUS_FAILED,
    PROCESSING_STATUS_SUCCESS
    )


class KoppeltaalException(Exception):
    def __init__(self, message):
        self.message = message


# XXX Cross-reference with http://www.hl7.org/fhir/resourcelist.html

# XXX (jw) I'd really would like to integrate the SMART-on-FHIR fhirclient
# Python library for realizing data into FHIR model objects. This would mean
# using JSON as transportation format though. Not a big deal perhaps?

class IConnector(zope.interface.Interface):

    server = zope.interface.Attribute('server base URL')

    domain = zope.interface.Attribute('domain')

    def metadata():
        pass

    def test_authentication():
        pass

    def activity_definition():
        pass

    def post_message(xml):
        pass

    def launch(activity_id, patient_url, user_url):
        pass

    def messsage(
            patient_url, processing_status=None, summary=False, count=5000):
        """Fetch messages.

        This will return a Bundle of MessageHeaders, allowing an application
        to browse the available messages. A pagesize can be specified in the
        count argument.

        The following additional arguments can be specified:

        patient_url: filters on the Patient dossier this message belongs

        processing_status: filters on the ProcessingStatus
        (New|Claimed|Success|Failed).

        summary: summarizes output. True or False.

        """

    def message(id):
        """Fetch single message."""

    def claim(id):
        pass

    def success(id):
        pass


class IName(zope.interface.Interface):

    given = zope.interface.Attribute('given name')

    family = zope.interface.Attribute('familiy name')


class INamed(zope.interface.Interface):

    name = zope.interface.Attribute('IName')


class IFHIRResource(zope.interface.Interface):
    """Marker interface for a resource that is defined in "standard" FHIR.

    """


class IResource(IFHIRResource):

    __node__ = zope.interface.Attribute(
        'XML node representing this resource. Can be ``None``.')

    __version__ = zope.interface.Attribute(
        'Koppeltaal version specifier for this resource. Can be ``None``.')


class IPatient(IResource, INamed):
    pass


class IPractitioner(IResource, INamed):
    pass


class IMessageHeader(IResource):

    status = zope.interface.Attribute('processing status')

    reference = zope.interface.Attribute(
        'focal resource reference, with version')


class ICarePlan(IResource):

    patient = zope.interface.Attribute('IPatient')


class IActivity(IResource):

    identifier = zope.interface.Attribute(
        'ActivityDefinition#ActivityDefinitionIdentifier')

    name = zope.interface.Attribute('ActivityDefinition#ActivityName')

    kind = zope.interface.Attribute('ActivityDefinition#ActivityKind')
