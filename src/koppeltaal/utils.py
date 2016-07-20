import ConfigParser
import datetime
import uuid
import os.path


class UTC(datetime.tzinfo):

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)

utc = UTC()


def strip_history_from_link(link):
    return link.split('/_history/', 1)[0]


def json2links(data):
    links = {}
    for link in data.get('link', []):
        links[link['rel']] = link['href']
    return links


def uniqueid():
    """Generate a unique ID.
    """
    return unicode(uuid.uuid4())


def messageid():
    """Generate a unique ID for a new message.
    """
    return uniqueid()


def now():
    return datetime.datetime.utcnow().replace(microsecond=0, tzinfo=utc)


def get_credentials_from_file(server):
    # They're not passed in, so now look at ~/.koppeltaal.cfg.
    parser = ConfigParser.ConfigParser()
    parser.read(os.path.expanduser('~/.koppeltaal.cfg'))
    if not parser.has_section(server):
        raise ValueError('No user credentials found in ~/.koppeltaal.cfg')
    username = parser.get(server, 'username')
    password = parser.get(server, 'password')
    domain = parser.get(server, 'domain')
    if not username or not password or not domain:
        raise ValueError('No user credentials found in ~/.koppeltaal.cfg')
    return username, password, domain
