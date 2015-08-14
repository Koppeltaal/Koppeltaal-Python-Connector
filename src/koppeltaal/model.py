"""
FHIR-like models.
XXX Cross-reference with http://www.hl7.org/fhir/resourcelist.html
"""
import koppeltaal


class Name(object):
    given = family = None


class Patient(object):

    def __init__(self, id, url):
        self.id = id
        self.url = url
        self.name = Name()


class CarePlan(object):

    def __init__(self, id, url, patient):
        self.id = id
        self.url = url
        self.patient = patient


class Practitioner(object):

    def __init__(self, id, url):
        self.id = id
        self.url = url
        self.name = Name()


class Resource(object):

    id = node = None

    def __init__(self, id, node):
        self.id = id
        self.node = node


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


class CarePlanResult(object):

    def __init__(self, reference):
        self.reference = reference


class Activity(object):

    def __init__(self, id, name, kind):
        self.id = id
        self.name = name
        self.kind = kind
