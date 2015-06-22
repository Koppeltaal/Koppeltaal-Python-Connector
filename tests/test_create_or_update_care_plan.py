import lxml.etree
import pytest
import py.path
import koppeltaal

import feedreader.parser
from koppeltaal.activity_definition import activity_info
from koppeltaal.create_or_update_care_plan import generate
from koppeltaal_schema.validate import validate

here = py.path.local(__file__)
sample_feed = (here.dirpath() / 'fixtures/sample_activity_definition.xml').read()


class Name(object):
    given = family = None


class Patient(object):
    id = url = name = None

    def __init__(self):
        self.name = Name()


class CarePlan(object):
    id = url = None


class Practitioner(object):
    id = url = None

    def __init__(self):
        self.name = Name()


pat1 = Patient()
pat1.id = '1'
pat1.url = 'http://example.com/patient/1'
pat1.name.given = 'Claes'
pat1.name.family = 'de Vries'

cp2 = CarePlan()
cp2.id = '2'
cp2.url = 'http://example.com/patient/1/careplan/2'

prac_a = Practitioner()
prac_a.id = 'a'
prac_a.url = 'http://example.com/practitioner/a'
prac_a.name.given = 'Jozef'
prac_a.name.family = 'van Buuren'


def find_link(entry):
    # Ugly python, need to escape the {} to use .format().
    for link in entry._xml.iterchildren(tag='{%(atom)s}link' % koppeltaal.NS):
        if link.attrib.get('rel') == 'self':
            return link.attrib['href']


def test_create_or_update_care_plan():
    activity = activity_info(sample_feed, 'AD1')

    result = generate(
        'foo',
        activity,
        # patient
        pat1,
        # careplan
        cp2,
        # practitioner
        prac_a)

    node = lxml.etree.fromstring(result)
    # Validate.
    assert validate(node) is None

    # Dogfooding here; parse as atom feed.
    feed = feedreader.parser.from_string(result)
    assert len(feed.entries) == 4

    security_category = node.find(
        'atom:category[@scheme="{fhir}/tag"]'.format(**koppeltaal.NS),
        namespaces=koppeltaal.NS)
    assert security_category.get('term') == '{fhir}/tag/message'.format(
        **koppeltaal.NS)

    domain_category = node.find(
        'atom:category[@scheme="{fhir}/tag/security"]'.format(**koppeltaal.NS),
        namespaces=koppeltaal.NS)
    assert domain_category.get('label') == 'foo'

    # XXX Use the feed reader instead of xpath

    # inspect message header
    messageheader_entry = feed.entries[0]

    # Can't use feed.entries[x].link here, the feedreader code doesn't
    # know about "self". Perhaps fix this or use another feedreader component.
    assert find_link(messageheader_entry) is None
    messageheader = messageheader_entry.content.find(
        'fhir:MessageHeader', namespaces=koppeltaal.NS)
    # The message header mentions the Patient.
    assert messageheader.find(
        'fhir:extension[@url="{koppeltaal}/MessageHeader#Patient"]'.format(
        **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:valueResource', namespaces=koppeltaal.NS).find(
            'fhir:reference', namespaces=koppeltaal.NS).get('value') == pat1.url

    # inspect careplan
    assert find_link(feed.entries[1]) == cp2.url
    careplan = node.xpath('//fhir:CarePlan', namespaces=koppeltaal.NS)[0]
    activity_id = careplan.xpath(
        '//fhir:activity/fhir:extension/fhir:valueString',
        namespaces=koppeltaal.NS)[0].get('value')
    assert activity_id == 'AD1'
    activity_code = careplan.xpath(
        '//fhir:activity/fhir:extension/fhir:valueCoding/fhir:code',
        namespaces=koppeltaal.NS)[0].get('value')
    assert activity_code == 'Game'

    # inspect patient
    assert find_link(feed.entries[2]) == pat1.url
    patient = node.xpath('//fhir:Patient', namespaces=koppeltaal.NS)[0]
    patient_name = patient.find('fhir:name', namespaces=koppeltaal.NS)
    assert patient_name.find(
        'fhir:given', namespaces=koppeltaal.NS).get('value') == 'Claes'
    assert patient_name.find(
        'fhir:family', namespaces=koppeltaal.NS).get('value') == 'de Vries'

    # inspect practitioner
    assert find_link(feed.entries[3]) == prac_a.url
    practitioner = node.xpath('//fhir:Practitioner', namespaces=koppeltaal.NS)[0]
    practitioner_name = practitioner.find('fhir:name', namespaces=koppeltaal.NS)
    assert practitioner_name.find(
        'fhir:given', namespaces=koppeltaal.NS).get('value') == 'Jozef'
    assert practitioner_name.find(
        'fhir:family', namespaces=koppeltaal.NS).get('value') == 'van Buuren'


@pytest.mark.xfail(
    reason='The server sends back a 405, which is not what we expect.')
def test_send_create_or_update_care_plan_to_server(connector):
    """
    Send a careplan to the server and check that there is a message in the
    mailbox.
    """
    from random import randint
    from koppeltaal.activity_definition import parse
    # A random activity, could be anything.
    first_activity = list(parse(connector.activity_definition()))[0]

    pat1 = Patient()
    pat1.id = '1'
    pat1.url = 'http://example.com/patient/1'
    pat1.name.given = 'Claes'
    pat1.name.family = 'de Vries'

    cp2 = CarePlan()
    cp2.id = str(randint(100000000000, 10000000000000000))
    cp2.url = 'http://example.com/patient/1/careplan/{}'.format(cp2.id)

    prac_a = Practitioner()
    prac_a.id = 'a'
    prac_a.url = 'http://example.com/practitioner/a'
    prac_a.name.given = 'Jozef'
    prac_a.name.family = 'van Buuren'

    xml = generate(
        connector.domain,
        first_activity,
        pat1,
        cp2,
        prac_a)

    # XXX Fails with a 405.
    result = connector.create_or_update_care_plan(xml)

    # XXX Assert there is a message in the mailbox.


# XXX test non-existing activity definition, should return an error from the
# server.
