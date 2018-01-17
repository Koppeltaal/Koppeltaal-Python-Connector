# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import collections
import datetime
import os.path
import six
import uuid

from configparser import ConfigParser
from six.moves.urllib.parse import urlparse


unicode = six.text_type


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


Credentials = collections.namedtuple(
    'Credentials',
    ['url', 'username', 'password', 'domain', 'options'])


def get_credentials_from_file(name):
    # They're not passed in, so now look at ~/.koppeltaal.cfg.
    config = unicode(os.path.expanduser('~/.koppeltaal.cfg'))
    if not os.path.isfile(config):
        raise ValueError("Can't find ~/.koppeltaal.cfg")
    parser = ConfigParser()
    parser.read(config)
    if not parser.has_section(name):
        raise ValueError('No user credentials found in ~/.koppeltaal.cfg')
    url = parser.get(name, 'url')
    parsed = urlparse(url)
    if parsed.scheme != 'https' or \
            parsed.netloc == '' or \
            parsed.path != '' or \
            parsed.params != '' or \
            parsed.query != '' or \
            parsed.fragment != '':
        raise ValueError('Incorrect server URL.')
    username = parser.get(name, 'username')
    password = parser.get(name, 'password')
    domain = parser.get(name, 'domain')
    if not username or not password or not domain:
        raise ValueError('No user credentials found in ~/.koppeltaal.cfg')
    return Credentials(
        url, username, password, domain,
        dict(parser.items(name)))
