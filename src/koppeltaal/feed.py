import feedreader.parser
import koppeltaal
import koppeltaal.feed
import koppeltaal.model


# Move this parsing to the python package "feedreader".
def find_link(entry):
    for link in entry._xml.iterchildren(
            tag='{{{atom}}}link'.format(**koppeltaal.NS)):
        if link.attrib.get('rel') == 'self':
            return link.attrib['href']


# Ideally, a better registration mechanism here.
RESOURCE_LOOKUP = {
    '{{{fhir}}}MessageHeader'.format(
        **koppeltaal.NS): koppeltaal.model.MessageHeader
}


def parse(xml):
    # <totalResults xmlns="http://a9.com/-/spec/opensearch/1.1/">
    # 1</totalResults>
    feed = feedreader.parser.from_string(xml)
    for entry in feed.entries:
        assert len(entry.content) == 1, \
            'there should be only one content node in {}'.format(xml)
        first_child = entry.content.getchildren()[0]
        # Default value is Resource.
        factory = RESOURCE_LOOKUP.get(
            first_child.tag, koppeltaal.model.Resource)
        yield factory(find_link(entry), first_child)
