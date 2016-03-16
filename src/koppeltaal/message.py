import re
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
    return None if not links else links[0].attrib['href']


def extensions(
        node, ext,
        _expr=lxml.etree.XPath('./fhir:extension[@url=$ext]', namespaces=NS)):
    found = _expr(node, ext=ext)
    return None if not found else found


def extension(node, ext):
    found = extensions(node, ext)
    if found is None:
        return None
    return None if not found else found[0]


def valuestring(
        node,
        _expr=lxml.etree.XPath('./fhir:valueString/@value', namespaces=NS)):
    found = _expr(node)
    return None if not found else found[0]


def valueinteger(
        node,
        _expr=lxml.etree.XPath('./fhir:valueInteger/@value', namespaces=NS)):
    found = _expr(node)
    return None if not found else int(found[0])


def valuecode(
        node,
        _expr=lxml.etree.XPath('./fhir:valueCode/@value', namespaces=NS)):
    found = _expr(node)
    return None if not found else found[0]


def valuecoding(
        node,
        _expr=lxml.etree.XPath('./fhir:valueCoding', namespaces=NS)):
    coding = _expr(node)[0]
    system = coding.xpath('./fhir:system/@value', namespaces=NS)[0]
    code = coding.xpath('./fhir:code/@value', namespaces=NS)[0]
    display = coding.xpath('./fhir:display/@value', namespaces=NS)[0]
    return (system, code, display)


def valueresourcereference(
        node,
        _expr=lxml.etree.XPath(
            './fhir:valueResource/fhir:reference/@value', namespaces=NS)):
    refs = _expr(node)
    return None if not refs else refs[0]


EXTRACTORS = {
    '{{{fhir}}}valueCode'.format(**NS): valuecode,
    '{{{fhir}}}valueCoding'.format(**NS): valuecoding,
    '{{{fhir}}}valueInteger'.format(**NS): valueinteger,
    '{{{fhir}}}valueResource'.format(**NS): valueresourcereference,
    '{{{fhir}}}valueString'.format(**NS): valuestring,
    }


def extract(node):
    childs = node.xpath('./*')
    if not childs:
        return None
    child = childs[0]
    extractor = EXTRACTORS.get(child.tag)
    return extractor(node) if extractor else None


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
        return self.__node__.xpath(
            './fhir:event/fhir:code', namespaces=NS)[0].attrib['value']

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


def get_new_messageheaders(conn, patient=None, filter=None, _batchsize=1000):
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

    if filter is None:
        filter = lambda x: True

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

    return (hdr for hdr in _message_headers() if filter(hdr))


@zope.interface.implementer(koppeltaal.interfaces.ICarePlan)
class CarePlan(koppeltaal.model.Resource):

    # XXX probably wrong place for this model-like class.

    activityid_ext = '{koppeltaal}/CarePlan#ActivityIdentifier'.format(**NS)
    activitystatus_ext = '{koppeltaal}/CarePlan#ActivityStatus'.format(**NS)
    subactivity_ext = '{koppeltaal}/CarePlan#SubActivity'.format(**NS)

    @classmethod
    def from_entry(cls, entry):
        return cls(
            node=entry.xpath(
                './atom:content/fhir:CarePlan', namespaces=NS)[0],
            version=link(entry, rel='self'))

    def activity_status(self):
        return valuecoding(
            extension(self.__node__, self.activitystatus_ext))

    def sub_activities(self):
        return [
            valuestring(n) for n in
            extensions(self.__node__, self.subactivity_ext)]


@zope.interface.implementer(koppeltaal.interfaces.IResource)
class Other(koppeltaal.model.Resource):

    # XXX probably wrong place for this model-like class.

    @classmethod
    def from_entry(cls, entry):
        return cls(
            node=entry.xpath(
                './atom:content/fhir:Other', namespaces=NS)[0],
            version=link(entry, rel='self'))

    def extract_data(self, ext):
        found = extensions(self.__node__, '{koppeltaal}/{}'.format(ext, **NS))
        if found is None:
            return None
        return [extract(node) for node in found]


@zope.interface.implementer(koppeltaal.interfaces.IMessage)
class Message(koppeltaal.model.Resource):

    # NOTE there is not really a message-like element in the FHIR-over-Atom
    # modelling. For us here it is the Atom feed with MessageHeader element,
    # CarePlan element and Patient and Practitioner elements.

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
        found = self.__node__.xpath(
            './atom:entry[./atom:content/fhir:CarePlan]', namespaces=NS)
        return None if not found else CarePlan.from_entry(found[0])

    def other(self):
        found = self.__node__.xpath(
            './atom:entry[./atom:content/fhir:Other]', namespaces=NS)
        return None if not found else Other.from_entry(found[0])


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


# XXX this feel rather like circular reasoning, but API-wise I think I'm
# somewhat on the right track.


def claim_message(conn, messageheader):
    conn.claim(messageheader.__version__)
    return get_message(conn, messageheader)


def success_message(conn, messageheader):
    conn.success(messageheader.__version__)
    return get_message(conn, messageheader)


def version_split(spec, expr=re.compile('^(https://.*)/(_history/.*)$')):

    # XXX probably not the right location for this helper.

    match = expr.match(spec)
    return match.group(1, 2)  # XXX fails for non-version input. can be nicer.
