"""
Work with FHIR Messages.
"""
import feedreader.parser
import koppeltaal
import koppeltaal.feed

# XXX Not happy about the names here yet.

def parse_messages(xml):
    # XXX total messages.
    # <totalResults xmlns="http://a9.com/-/spec/opensearch/1.1/">1</totalResults>
    #
    # id, processing status per message
    feed = feedreader.parser.from_string(xml)
    for entry in feed.entries:
        self_link = koppeltaal.feed.find_link(entry)
        # Bart Mehlkop said:
        #
        # De ID is op dit moment alleen nog te vinden door de self-link te
        # parsen:
        #
        # In bijvoorbeeld:
        # <link rel="self"
        # href="https://testconnectors.vhscloud.nl/FHIR/Koppeltaal/MessageHeader/401/_history/2015-06-25T16:19:42:054.4163"
        # />
        #
        # is de ID '401'.
        assert self_link, 'need a link to refer to this message'
        split_link = self_link.split('/')
        message_id = split_link[split_link.index('MessageHeader') + 1]

        processing_status = entry.content.find(
            'fhir:MessageHeader', namespaces=koppeltaal.NS).find(
            'fhir:extension[@url="{koppeltaal}/MessageHeader#ProcessingStatus"]'.format(
                **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:extension[@url="{koppeltaal}/MessageHeader#ProcessingStatusStatus"]'.format(
                **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:valueCode', namespaces=koppeltaal.NS).get('value')

        yield koppeltaal.model.Message(message_id, processing_status)


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
