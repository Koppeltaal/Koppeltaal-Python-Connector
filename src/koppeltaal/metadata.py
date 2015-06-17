import lxml.etree
import koppeltaal


def metadata(xml):
    """
    Given a Conformance statement,
    extract the relevant information.
    """
    node = lxml.etree.fromstring(xml)

    messaging = node.find('fhir:messaging', namespaces=koppeltaal.NS)
    return {
        'messaging': {
            'endpoint': messaging.find(
                'fhir:endpoint', namespaces=koppeltaal.NS).get('value')
        }
    }
