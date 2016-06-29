"""FHIR-like models."""
import zope.interface
import koppeltaal
import koppeltaal.interfaces


@zope.interface.implementer(koppeltaal.interfaces.IName)
class Name(object):
    given = family = None


@zope.interface.implementer(koppeltaal.interfaces.IResource)
class Resource(object):

    __node__ = None
    __version__ = None

    def __init__(self, node=None, version=None):
        self.__node__ = node
        self.__version__ = version


@zope.interface.implementer(koppeltaal.interfaces.IPatient)
class Patient(Resource):

    def __init__(self, node=None, version=None):
        super(Patient, self).__init__(node, version)
        self.name = Name()


@zope.interface.implementer(koppeltaal.interfaces.IPractitioner)
class Practitioner(Resource):

    def __init__(self, node=None, version=None):
        super(Practitioner, self).__init__(node, version)
        self.name = Name()


@zope.interface.implementer(koppeltaal.interfaces.IMessageHeader)
class MessageHeader(Resource):

    @property
    def reference(self):
        if self.__node__ is None:
            return None

    @property
    def status(self):
        return self.__node__.find(
            'fhir:extension['
            '@url="{koppeltaal}/MessageHeader#ProcessingStatus"]'.format(
                **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:extension['
            '@url="{koppeltaal}/MessageHeader#ProcessingStatusStatus"]'.format(
                **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:valueCode', namespaces=koppeltaal.NS).get('value')

    @status.setter
    def status(self, value):
        # This is a mutation of the underlying node.
        self.__node__.find(
            './/fhir:extension[@url="{koppeltaal}/MessageHeader#'
            'ProcessingStatusStatus"]'.format(
                **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:valueCode', namespaces=koppeltaal.NS).attrib['value'] = value


@zope.interface.implementer(koppeltaal.interfaces.ICarePlan)
class CarePlan(Resource):

    def __init__(self, patient, node=None, version=None):
        super(CarePlan, self).__init__(node, version)
        self.patient = patient


@zope.interface.implementer(koppeltaal.interfaces.IActivity)
class Activity(Resource):

    def __init__(self, identifier, kind, name):
        self.identifier = identifier
        self.name = name
        self.kind = kind
