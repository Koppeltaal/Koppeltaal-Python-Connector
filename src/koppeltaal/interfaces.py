import zope.interface

NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'fhir': 'http://hl7.org/fhir',
    'koppeltaal': 'http://ggz.koppeltaal.nl/fhir/Koppeltaal',
    }


class KoppeltaalException(Exception):
    def __init__(self, message):
        self.message = message


# XXX Cross-reference with http://www.hl7.org/fhir/resourcelist.html


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

    def message_process(id, action=None, status=None):
        pass


class IName(zope.interface.Interface):

    given = zope.interface.Attribute('given name')

    family = zope.interface.Attribute('familiy name')


class IEntity(zope.interface.Interface):

    id = zope.interface.Attribute('id')

    url = zope.interface.Attribute('URL')


class INamed(zope.interface.Interface):

    name = zope.interface.Attribute('IName')


class IPatient(IEntity, INamed):
    pass


class IPractitioner(IEntity, INamed):
    pass


class ICarePlan(IEntity):

    patient = zope.interface.Attribute('IPatient')


class IResource(zope.interface.Interface):

    id = zope.interface.Attribute('id')

    node = zope.interface.Attribute('node')


class IMessageHeader(IResource):

    processing_status = zope.interface.Attribute('processing status')


class ICarePlanResult(zope.interface.Interface):

    reference = zope.interface.Attribute('reference')


class IActivity(zope.interface.Interface):

    id = zope.interface.Attribute('id')

    name = zope.interface.Attribute('name')

    kind = zope.interface.Attribute('kind')
