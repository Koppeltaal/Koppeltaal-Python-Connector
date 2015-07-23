"""
FHIR-like models.
XXX Cross-reference with http://www.hl7.org/fhir/resourcelist.html
"""


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


class Message(object):

    def __init__(self, entry, id, status):
        self.entry = entry
        self.id = id
        self.status = status


class CarePlanResult(object):

    def __init__(self, reference):
        self.reference = reference


class Activity(object):

    def __init__(self, node, id, name, kind):
        self.node = node
        self.id = id
        self.name = name
        self.kind = kind
