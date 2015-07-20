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

    def __init__(self, id, url):
        self.id = id
        self.url = url


class Practitioner(object):

    def __init__(self, id, url):
        self.id = id
        self.url = url
        self.name = Name()


class Message(object):

    def __init__(self, id, status):
        self.id = id
        self.status = status
