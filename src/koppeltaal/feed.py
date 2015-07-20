import koppeltaal

# XXX Move to feedparser.
def find_link(entry):
    # Ugly python, need to escape the {} to use .format().
    for link in entry._xml.iterchildren(tag='{%(atom)s}link' % koppeltaal.NS):
        if link.attrib.get('rel') == 'self':
            return link.attrib['href']

