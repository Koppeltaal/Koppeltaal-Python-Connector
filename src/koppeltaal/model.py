"""FHIR-like models."""
import zope.interface
import koppeltaal
import koppeltaal.interfaces


@zope.interface.implementer(koppeltaal.interfaces.IName)
class Name(object):
    given = family = None


@zope.interface.implementer(koppeltaal.interfaces.IPatient)
class Patient(object):

    def __init__(self, id, url):
        self.id = id
        self.url = url
        self.name = Name()


@zope.interface.implementer(koppeltaal.interfaces.IPractitioner)
class Practitioner(object):

    def __init__(self, id, url):
        self.id = id
        self.url = url
        self.name = Name()


@zope.interface.implementer(koppeltaal.interfaces.ICarePlan)
class CarePlan(object):

    def __init__(self, id, url, patient):
        self.id = id
        self.url = url
        self.patient = patient


@zope.interface.implementer(koppeltaal.interfaces.IResource)
class Resource(object):

    id = node = None

    def __init__(self, id, node):
        self.id = id
        self.node = node


@zope.interface.implementer(koppeltaal.interfaces.IMessageHeader)
class MessageHeader(Resource):

    @property
    def processing_status(self):
        return self.node.find(
            'fhir:extension['
            '@url="{koppeltaal}/MessageHeader#ProcessingStatus"]'.format(
                **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:extension['
            '@url="{koppeltaal}/MessageHeader#ProcessingStatusStatus"]'.format(
                **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:valueCode', namespaces=koppeltaal.NS).get('value')

    @processing_status.setter
    def processing_status(self, value):
        # This is a mutation of the underlying node.
        self.node.find(
            './/fhir:extension[@url="{koppeltaal}/MessageHeader#'
            'ProcessingStatusStatus"]'.format(
                **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:valueCode', namespaces=koppeltaal.NS).attrib['value'] = value


@zope.interface.implementer(koppeltaal.interfaces.ICarePlanResult)
class CarePlanResult(object):

    def __init__(self, reference):
        self.reference = reference


@zope.interface.implementer(koppeltaal.interfaces.IActivity)
class Activity(object):

    def __init__(self, id, name, kind):
        self.id = id
        self.name = name
        self.kind = kind
