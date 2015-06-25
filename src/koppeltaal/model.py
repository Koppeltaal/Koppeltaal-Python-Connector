"""
FHIR-like models.
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
