

def strip_history_from_link(link):
    return link.split('/_history/', 1)[0]


def json2links(data):
    links = {}
    for link in data.get('link', []):
        links[link['rel']] = link['href']
    return links
