import lxml.etree
import pytest
import requests
import py.path
import koppeltaal
import koppeltaal.feed

here = py.path.local(__file__)
sample_feed = (here.dirpath() / 'fixtures/sample_activity_definition.xml').read()


def test_create_or_update_care_plan():
    from koppeltaal.model import Patient, Practitioner, CarePlan
    from koppeltaal.create_or_update_care_plan import generate
    from koppeltaal_schema.validate import validate
    from koppeltaal.activity_definition import activity_info
    import feedreader.parser

    activity = activity_info(sample_feed, 'AD1')

    pat1 = Patient('1', 'http://example.com/patient/1')
    pat1.name.given = 'Claes'
    pat1.name.family = 'de Vries'

    cp2 = CarePlan('2', 'http://example.com/patient/1/careplan/2', pat1)

    prac_a = Practitioner('a', 'http://example.com/practitioner/a')
    prac_a.name.given = 'Jozef'
    prac_a.name.family = 'van Buuren'

    result = generate('foo', activity, pat1, cp2, prac_a)

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
    assert koppeltaal.feed.find_link(messageheader_entry) is None
    messageheader = messageheader_entry.content.find(
        'fhir:MessageHeader', namespaces=koppeltaal.NS)
    # The message header mentions the Patient.
    assert messageheader.find(
        'fhir:extension[@url="{koppeltaal}/MessageHeader#Patient"]'.format(
        **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:valueResource', namespaces=koppeltaal.NS).find(
            'fhir:reference', namespaces=koppeltaal.NS).get('value') == pat1.url

    # inspect careplan
    assert koppeltaal.feed.find_link(feed.entries[1]) == cp2.url
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
    assert koppeltaal.feed.find_link(feed.entries[2]) == pat1.url
    patient = node.xpath('//fhir:Patient', namespaces=koppeltaal.NS)[0]
    patient_name = patient.find('fhir:name', namespaces=koppeltaal.NS)
    assert patient_name.find(
        'fhir:given', namespaces=koppeltaal.NS).get('value') == 'Claes'
    assert patient_name.find(
        'fhir:family', namespaces=koppeltaal.NS).get('value') == 'de Vries'

    # inspect practitioner
    assert koppeltaal.feed.find_link(feed.entries[3]) == prac_a.url
    practitioner = node.xpath('//fhir:Practitioner', namespaces=koppeltaal.NS)[0]
    practitioner_name = practitioner.find('fhir:name', namespaces=koppeltaal.NS)
    assert practitioner_name.find(
        'fhir:given', namespaces=koppeltaal.NS).get('value') == 'Jozef'
    assert practitioner_name.find(
        'fhir:family', namespaces=koppeltaal.NS).get('value') == 'van Buuren'


def test_send_care_plan_to_server(
        connector, patient, practitioner, careplan, activity):
    """
    Send a careplan to the server and check that there is a message in the
    mailbox.
    """
    from koppeltaal.create_or_update_care_plan import generate, parse_result
    from koppeltaal.message import parse_messages

    # Before the careplan is sent, there are no messages for the patient.
    messages_for_pat = list(parse_messages(
        connector.messages(patient_url=patient.url)))
    assert len(messages_for_pat) == 0

    xml = generate(connector.domain, activity, patient, careplan, practitioner)
    result = connector.post_message(xml)

    # The careplan was sent successfully and now has a _history.
    assert careplan.url in parse_result(result).reference

    # Assert there is a message in the mailbox for this patient.
    messages_for_pat = list(parse_messages(
        connector.messages(patient_url=patient.url)))
    assert len(messages_for_pat) == 1


def test_update_existing_care_plan(
        connector, patient, practitioner, practitioner2, careplan, activity):
    """
    Update an existing careplan, the history identifier is taken into account.
    """
    from koppeltaal.create_or_update_care_plan import generate, parse_result
    from koppeltaal.message import parse_messages

    # Before the careplan is sent, there are no messages for the patient.
    messages_for_pat = list(parse_messages(
        connector.messages(patient_url=patient.url)))
    assert len(messages_for_pat) == 0

    xml = generate(connector.domain, activity, patient, careplan, practitioner)
    result = connector.post_message(xml)

    # The careplan was sent successfully and now has a _history.
    historic_careplan_url = parse_result(result).reference
    assert careplan.url in historic_careplan_url

    # If we now create a careplan with a different practitioner, this will
    # yield an error, because we are not injecting the historic information.
    xml = generate(connector.domain, activity, patient, careplan, practitioner2)
    # XXX This should be a Koppeltaal Exception, and on the server this should
    # be a 400 instead of a 500, because the request is wrong.
    with pytest.raises(requests.HTTPError) as excinfo:
        connector.post_message(xml)
    assert "No version specfied for the focal resource, message is rejected." in excinfo.value.response.text

    # When setting the care plan url from the server to the current careplan,
    # we can generate the XML properly.
    careplan.url = historic_careplan_url
    xml = generate(connector.domain, activity, patient, careplan, practitioner2)
    result = connector.post_message(xml)

    # The careplan was sent successfully and now has a _history.
    historic_careplan_url_2 = parse_result(result).reference
    # Using string comparison on date strings is ok here. The second careplan
    # accepted by the server has a later dt than the first one.
    assert historic_careplan_url_2 > historic_careplan_url

    # We *do* need to use the _history URL, we can't just
    # fabricate a URL by interpolating the current timestamp.
    import datetime
    now_url = '{}/{}'.format(
        '/'.join(historic_careplan_url_2.split('/')[:-1]),
        datetime.datetime.utcnow().isoformat())
    careplan.url = now_url
    xml = generate(connector.domain, activity, patient, careplan, practitioner)
    with pytest.raises(requests.HTTPError) as excinfo:
        connector.post_message(xml)
    assert "Message Version mismatch: Please retrieve the latest version" in excinfo.value.response.text


@pytest.mark.xfail(reason=
    'The call to the koppeltaal server with an unknown careplan '
    'activity id does not fail.')
def test_send_incorrect_careplan_expect_failure(
        connector, patient, practitioner, careplan):
    '''When sending a careplan with a non-existing activity definition,
    the server should return an error.'''
    from koppeltaal.activity_definition import parse
    from koppeltaal.create_or_update_care_plan import generate
    from koppeltaal import KoppeltaalException

    funky_activity = list(parse(connector.activity_definition()))[0]
    # Unknown activity, should fail.
    funky_activity['identifier'] = 'foobar'
    xml = generate(connector.domain, funky_activity, patient, careplan, practitioner)
    with pytest.raises(KoppeltaalException):
        connector.post_message(xml)
