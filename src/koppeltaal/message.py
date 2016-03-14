import lxml.etree
import requests
import feedreader
import zope.interface
import koppeltaal.interfaces
import koppeltaal.model


NS = koppeltaal.interfaces.NS


def link(
        node, rel='self',
        _expr=lxml.etree.XPath('./atom:link[@rel=$rel]', namespaces=NS)):
    links = _expr(node, rel=rel)
    if not links:
        return None
    return links[0].attrib['href']


def extension(
        node, ext,
        _expr=lxml.etree.XPath('./fhir:extension[@url=$ext]', namespaces=NS)):
    extensions = _expr(node, ext=ext)
    if not extensions:
        return None
    return extensions[0]


def valuestring(
        node,
        _expr=lxml.etree.XPath('./fhir:valueString/@value', namespaces=NS)):
    values = _expr(node)
    if not values:
        return None
    return values[0]


def valuecode(
        node,
        _expr=lxml.etree.XPath('./fhir:valueCode/@value', namespaces=NS)):
    codes = _expr(node)
    if not codes:
        return None
    return codes[0]


def valueresourcereference(
        node,
        _expr=lxml.etree.XPath(
            './fhir:valueResource/fhir:reference/@value', namespaces=NS)):
    refs = _expr(node)
    if not refs:
        return None
    return refs[0]


@zope.interface.implementer(koppeltaal.interfaces.IMessageHeader)
class MessageHeader(koppeltaal.model.Resource):

    patient_ext = '{koppeltaal}/MessageHeader#Patient'.format(**NS)
    status_ext = '{koppeltaal}/MessageHeader#ProcessingStatus'.format(**NS)
    statusstatus_ext = (
        '{koppeltaal}/MessageHeader#ProcessingStatusStatus').format(**NS)

    @classmethod
    def from_entry(cls, entry):
        return cls(
            node=entry.xpath(
                './atom:content/fhir:MessageHeader', namespaces=NS)[0],
            version=link(entry, rel='self'))

    def status(self):
        return valuecode(
            extension(
                extension(self.__node__, self.status_ext),
                self.statusstatus_ext))

    def event(self):
        pass

    def source(self):
        return self.__node__.xpath(
            './fhir:source/fhir:endpoint', namespaces=NS)[0].attrib['value']

    def patient(self):
        return valueresourcereference(
            extension(self.__node__, self.patient_ext))

    def focal_resource(self):
        return self.__node__.xpath(
            './fhir:data/fhir:reference', namespaces=NS)[0].attrib['value']


def batch_feed(xml):
    feed = feedreader.parser.from_string(xml)
    return (e._xml for e in feed.entries), link(feed._xml, rel='next')


def get_new_messageheaders(conn, patient=None, _batchsize=1000):
    start_url = '{}/{}/_search'.format(
        conn.server, koppeltaal.interfaces.MESSAGE_HEADER_URL)
    headers = {
        'Accept': 'application/xml'}
    parameters = {
        'ProcessingStatus': koppeltaal.interfaces.PROCESSING_STATUS_NEW,
        '_summary': 'true',
        '_count': _batchsize,
        }

    if patient is not None:
        parameters['Patient'] = koppeltaal.url(patient)

    def _message_headers():
        response = requests.get(
            start_url,
            auth=(conn.username, conn.password),
            headers=headers,
            params=parameters,
            allow_redirects=False)

        while True:
            response.raise_for_status()
            entries, next = batch_feed(response.content)
            for entry in entries:
                yield MessageHeader.from_entry(entry)
            if next is None:
                break
            # XXX for some reason the next link is http://... weird...
            url = next.replace('http://', 'https://')
            # Note how we do not need to pass on parameters in this request as
            # the next link should contain all necessary info.
            response = requests.get(
                url,
                auth=(conn.username, conn.password),
                headers=headers,
                allow_redirects=False)

    return iter(_message_headers())


@zope.interface.implementer(koppeltaal.interfaces.IMessage)
class Message(koppeltaal.model.Resource):

    careplan_ext = '{koppeltaal}/CarePlan#ActivityIdentifier'.format(**NS)

    @classmethod
    def from_feed(cls, feed):
        return cls(feed)

    def __init__(self, node):
        super(Message, self).__init__(node, version=None)

    def messageheader(self):
        return MessageHeader.from_entry(
            self.__node__.xpath(
                './atom:entry[./atom:content/fhir:MessageHeader]',
                namespaces=NS)[0])

    def careplan(self):
        return valuestring(
            extension(
                self.__node__.xpath(
                    './atom:entry/atom:content/fhir:CarePlan/'
                    'fhir:activity', namespaces=NS)[0],
                self.careplan_ext))


def get_message(conn, messageheader=None, identifier=None):
    start_url = '{}/{}/_search'.format(
        conn.server, koppeltaal.interfaces.MESSAGE_HEADER_URL)
    headers = {'Accept': 'application/xml'}

    if messageheader is None:
        parameters = {'_id': identifier}
    else:
        parameters = {'_id': messageheader.__version__}

    response = requests.get(
        start_url,
        auth=(conn.username, conn.password),
        headers=headers,
        params=parameters,
        allow_redirects=False)

    return Message.from_feed(lxml.etree.fromstring(response.content))


# XXX this feel rather circular reasoning, but API-wise I think I'm somewhat
# on the right track.


def claim_message(conn, message):
    conn.claim(message.messageheader().__version__)
    return get_message(conn, message.messageheader())


def success_message(conn, message):
    conn.success(message.messageheader().__version__)
    return get_message(conn, message.messageheader())
