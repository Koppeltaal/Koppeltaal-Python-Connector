

def json2links(data):
    links = {}
    for link in data.get('link', []):
        links[link['rel']] = link['href']
    return links
