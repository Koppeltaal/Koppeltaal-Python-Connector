"""
Work with FHIR Messages.
"""
import feedreader.parser
import koppeltaal


# XXX Not happy about the names here yet.
def parse_messages(xml):
    return feedreader.parser.from_string(xml)


def parse_feed(xml):
    """
    Pass in a raw feed for a message, will generate a list of activity
    information.
    """
    feed = feedreader.parser.from_string(xml)
    return {
        'reference': feed.entries[0].content.find(
            'fhir:MessageHeader', namespaces=koppeltaal.NS).find(
            'fhir:data', namespaces=koppeltaal.NS).find(
            'fhir:reference', namespaces=koppeltaal.NS).get('value')
    }
