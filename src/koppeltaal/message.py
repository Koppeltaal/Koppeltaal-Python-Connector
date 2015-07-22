"""
Work with FHIR Messages.
"""
import feedreader.parser
import lxml.etree
import requests
import koppeltaal
import koppeltaal.feed
import koppeltaal.connect

# XXX Not happy about the names here yet.


def parse_messages(xml):
    # XXX total messages.
    # <totalResults xmlns="http://a9.com/-/spec/opensearch/1.1/">
    # 1</totalResults>
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
            'fhir:extension['
            '@url="{koppeltaal}/MessageHeader#ProcessingStatus"]'.format(
                **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:extension['
            '@url="{koppeltaal}/MessageHeader#ProcessingStatusStatus"]'.format(
                **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:valueCode', namespaces=koppeltaal.NS).get('value')

        yield koppeltaal.model.Message(message_id, processing_status)


def process(connector, id, action):
    # Updating the ProcessingStatus for a Message - After a message
    # has been successfully processed, the application must update its
    # ProcessingStatus to "Success" on URL
    # [[|https://koppelbox/FHIR/Koppeltaal/MessageHeader/[id]]] (that
    # is, the URL returned as id link in the for the MessageHeader in
    # the bundle.)
    status = {
        'claim': 'Claimed',
        'success': 'Success'
    }.get(action, None)
    if status is None:
        raise ValueError('Unknown status')

    # Get the message.
    url = '{}/{}/_search'.format(
        connector.server, koppeltaal.connect.MESSAGE_HEADER_URL)
    response = requests.get(
        url,
        params={'_id': id},
        auth=(connector.username, connector.password),
        headers={'Accept': 'application/xml'},
        allow_redirects=False)
    response.raise_for_status()
    feed = feedreader.parser.from_string(response.content)
    # XXX How can you be so sure about nr 0.?
    message_header = feed.entries[0].content.find(
        './/fhir:MessageHeader', namespaces=koppeltaal.NS)
    # Parse the XML with lxml.etree and set the ProcessingStatus.
    processing_status = message_header.find(
        './/fhir:extension[@url="{koppeltaal}/MessageHeader#'
        'ProcessingStatusStatus"]'.format(
            **koppeltaal.NS), namespaces=koppeltaal.NS).find(
        'fhir:valueCode', namespaces=koppeltaal.NS)
    processing_status.attrib['value'] = status

    response = requests.put(
        feed.entries[0].id,
        data=lxml.etree.tostring(message_header),
        auth=(connector.username, connector.password),
        headers={'Accept': 'application/xml'},
        allow_redirects=False)
    response.raise_for_status()
    return response.content
