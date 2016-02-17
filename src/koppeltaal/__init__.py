import logging


logger = logging.getLogger('koppeltaal')


NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'fhir': 'http://hl7.org/fhir',
    'koppeltaal': 'http://ggz.koppeltaal.nl/fhir/Koppeltaal',
    }


class KoppeltaalException(Exception):

    def __init__(self, message):
        self.message = message
