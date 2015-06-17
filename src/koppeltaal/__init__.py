import logging


logger = logging.getLogger('koppeltaal')

NS = {
    'fhir': 'http://hl7.org/fhir',
    'koppeltaal': 'http://ggz.koppeltaal.nl/fhir/Koppeltaal',
    'atom': 'http://www.w3.org/2005/Atom',
}


class KoppeltaalException(Exception):

    def __init__(self, message):
        self.message = message
