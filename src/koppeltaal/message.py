"""
Work with FHIR Messages.
"""
import feedreader.parser
import koppeltaal
import koppeltaal.feed
import koppeltaal.connect

# Ideally, a better registration mechanism here.
RESOURCE_LOOKUP = {
    '{{{fhir}}}MessageHeader'.format(**koppeltaal.NS): koppeltaal.model.MessageHeader
}

# XXX Rename to parse_feed.
def parse_messages(xml):
    # XXX total messages.
    # <totalResults xmlns="http://a9.com/-/spec/opensearch/1.1/">
    # 1</totalResults>
    feed = feedreader.parser.from_string(xml)
    for entry in feed.entries:
        assert len(entry.content) == 1, \
            'there should be only one content node in {}'.format(xml)
        first_child = content=entry.content.getchildren()[0]
        # Ddefault value is Resource.
        factory = RESOURCE_LOOKUP.get(
            first_child.tag, koppeltaal.model.Resource)
        yield factory(koppeltaal.feed.find_link(entry), first_child)
