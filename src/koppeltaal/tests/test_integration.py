# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""
import pdb
import koppeltaal.interfaces
import koppeltaal.utils
import koppeltaal.models
import pytest
import requests
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.wait

from six.moves.urllib.parse import urlparse, parse_qs


def test_request_metadata(connector):
    result = connector.metadata()
    assert isinstance(result, dict)
    assert result.get('name') == 'Koppeltaal'
    assert result.get('version') >= 'v1.0'
    assert result.get('fhirVersion') == '0.0.82'


def wait_for_application(browser):
    # wait until the page redirect dance is over.
    selenium.webdriver.support.wait.WebDriverWait(
        browser, 10).until(lambda d: 'test.html' in d.current_url)


def login_with_oauth(browser):
    [b for b in browser.find_elements_by_tag_name('button') if
        b.text == 'log in with oauth'][0].click()
    selenium.webdriver.support.wait.WebDriverWait(
        browser, 10).until(
            EC.text_to_be_present_in_element(
                ('id', 'authorizationOutput'), 'access_token'))


def request_care_plan(browser):
    [b for b in browser.find_elements_by_tag_name('button') if
        b.text == 'request care plan'][0].click()
    selenium.webdriver.support.wait.WebDriverWait(
        browser, 10).until(
            EC.text_to_be_present_in_element(
                ('id', 'carePlanOutput'), 'reference'))


def parse_launch_url(url):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    return query.get('iss', [''])[0]


def test_launch_patient(
        connector, careplan, careplan_response, patient, browser):
    launch_url = connector.launch(careplan, user=patient)
    assert parse_launch_url(launch_url).startswith(connector.transport.server)

    # There is a 'login with oauth' button in the page, let's see what that
    # does.
    browser.get(launch_url)
    wait_for_application(browser)
    selenium.webdriver.support.wait.WebDriverWait(
        browser, 10).until(
            lambda d: browser.find_element_by_id('patientReference'))

    assert browser.find_element_by_id('patientReference').text == ''
    assert browser.find_element_by_id('userReference').text == ''

    login_with_oauth(browser)
    selenium.webdriver.support.wait.WebDriverWait(
        browser, 10).until(
            lambda d: browser.find_element_by_id('patientReference'))
    assert browser.find_element_by_id('patientReference').text == \
        careplan.patient.fhir_link
    assert browser.find_element_by_id('userReference').text == \
        careplan.patient.fhir_link


def test_launch_practitioner(
        connector, careplan, careplan_response, practitioner, browser):
    # There is a 'login with oauth' button in the page, let's see what that
    # does.
    launch_url = connector.launch(careplan, user=practitioner)
    assert parse_launch_url(launch_url).startswith(connector.transport.server)

    browser.get(launch_url)
    wait_for_application(browser)
    assert browser.find_element_by_id('patientReference').text == ''
    assert browser.find_element_by_id('userReference').text == ''

    login_with_oauth(browser)
    assert browser.find_element_by_id('patientReference').text == \
        careplan.patient.fhir_link
    assert browser.find_element_by_id('userReference').text == \
        practitioner.fhir_link


def test_sso(connector):
    connector.integration.client_id = 'MindDistrict'
    connector.integration.client_secret = \
        connector._credentials.options.get('oauth_secret')

    patient_link = (
        'https://app.minddistrict.com/fhir/Koppeltaal/Patient/1394433515')
    step_1 = connector.launch_from_parameters(
        'MindDistrict', patient_link, patient_link, 'KTSTESTGAME')

    parts = urlparse(step_1)
    query = parse_qs(parts.query)

    assert query['application_id'][0] == 'MindDistrict'
    assert query['launch_id'][0] != ''

    step_2 = connector.authorize_from_parameters(
        query['application_id'][0],
        query['launch_id'][0],
        'https://example.com/koppeltaalauth')

    step_6 = requests.get(
        step_2, allow_redirects=False).headers.get('Location')

    parts = urlparse(step_6)
    query = parse_qs(parts.query)

    token = connector.token_from_parameters(
        query['code'][0],
        'https://example.com/koppeltaalauth')

    assert 'access_token' in token
    assert 'refresh_token' in token

    assert 'domain' in token and token['domain'] == connector.domain
    assert 'expires_in' in token and token['expires_in'] == 3600
    assert 'patient' in token and token['patient'] == patient_link
    assert 'resource' in token and token['resource'] == 'KTSTESTGAME'
    assert 'scope' in token and token['scope'] == 'patient/*.read'
    assert 'token_type' in token and token['token_type'] == 'Bearer'
    assert 'user' in token and token['user'] == patient_link


def test_sso_intent(connector):
    connector.integration.client_id = 'MindDistrict'
    connector.integration.client_secret = \
        connector._credentials.options.get('oauth_secret')

    patient_link = (
        'https://app.minddistrict.com/fhir/Koppeltaal/Patient/1394433515')
    step_1 = connector.launch_from_parameters(
        'MindDistrict', patient_link, patient_link, 'KTSTESTGAME',
        intent='Do Something Nice For Me')

    parts = urlparse(step_1)
    query = parse_qs(parts.query)

    assert query['application_id'][0] == 'MindDistrict'
    assert query['launch_id'][0] != ''

    step_2 = connector.authorize_from_parameters(
        query['application_id'][0],
        query['launch_id'][0],
        'https://example.com/koppeltaalauth')

    step_6 = requests.get(
        step_2, allow_redirects=False).headers.get('Location')

    parts = urlparse(step_6)
    query = parse_qs(parts.query)

    token = connector.token_from_parameters(
        query['code'][0],
        'https://example.com/koppeltaalauth')

    assert 'access_token' in token
    assert 'refresh_token' in token

    assert 'domain' in token and token['domain'] == connector.domain
    assert 'expires_in' in token and token['expires_in'] == 3600
    assert 'patient' in token and token['patient'] == patient_link
    assert 'resource' in token and token['resource'] == 'KTSTESTGAME'
    assert 'scope' in token and token['scope'] == 'patient/*.read'
    assert 'token_type' in token and token['token_type'] == 'Bearer'
    assert 'user' in token and token['user'] == patient_link
    assert 'intent' in token and token['intent'] == 'Do Something Nice For Me'


def test_send_activity(connector):
    uuid = koppeltaal.utils.uniqueid()

    assert len(list(connector.activities())) == 1
    assert connector.activity(u'uuid://{}'.format(uuid)) is None

    application = koppeltaal.models.ReferredResource(
        display='Test Generated Application Reference {}'.format(uuid))
    ad = koppeltaal.models.ActivityDefinition(
        application=application,
        description=u'Test Generated AD {}'.format(uuid),
        identifier=u'uuid://{}'.format(uuid),
        kind='ELearning',
        name=u'Test Generated AD {}'.format(uuid),
        performer='Patient',
        subactivities=[])

    updated = connector.send_activity(ad)
    assert len(list(connector.activities())) == 2
    assert updated.fhir_link is not None
    assert updated.fhir_link.startswith(
        'https://edgekoppeltaal.vhscloud.nl/FHIR/Koppeltaal'
        '/Other/ActivityDefinition:')
    assert updated.is_active is True
    assert updated.is_archived is False

    fetched = connector.activity(u'uuid://{}'.format(uuid))
    assert updated.fhir_link == fetched.fhir_link

    updated.is_active = False
    updated.is_archived = True

    connector.send_activity(updated)
    assert updated.fhir_link != fetched.fhir_link
    assert updated.fhir_link > fetched.fhir_link
    assert updated.is_active is False
    assert updated.is_archived is True
    assert connector.activity(u'uuid://{}'.format(uuid)) is None

    assert len(list(connector.activities())) == 1


def test_send_versioned_focal_resource_careplan(connector, careplan):
    response = connector.send(
        'CreateOrUpdateCarePlan', careplan, careplan.patient)
    first_version = response[0].fhir_link
    assert careplan.fhir_link != first_version
    assert careplan.fhir_link == \
        koppeltaal.utils.strip_history_from_link(first_version)

    with pytest.raises(koppeltaal.interfaces.OperationOutcomeError) as info:
        # Sending an update to the CarePlan without a version, now that the
        # server gave it a version, fails.
        connector.send(
            'CreateOrUpdateCarePlan', careplan, careplan.patient)

    assert info.value.outcome.issue[0].details == (
        'No version specified for the focal resource, message is rejected.')

    # When we properly update the CarePlan's version (FHIR link), we can send
    # an update again. And we get the subsequent version for it.
    careplan.fhir_link = first_version
    response = connector.send(
        'CreateOrUpdateCarePlan', careplan, careplan.patient)
    second_version = response[0].fhir_link
    assert first_version != second_version
    assert koppeltaal.utils.strip_history_from_link(first_version) == \
        koppeltaal.utils.strip_history_from_link(second_version)

    # Reusing the earlier version results in an error.
    careplan.fhir_link = first_version
    with pytest.raises(koppeltaal.interfaces.OperationOutcomeError) as info:
        connector.send(
            'CreateOrUpdateCarePlan', careplan, careplan.patient)

    assert info.value.outcome.issue[0].details == (
        'The specified resource version is not correct')

    careplan.fhir_link = second_version
    response = connector.send(
        'CreateOrUpdateCarePlan', careplan, careplan.patient)
    third_version = response[0].fhir_link
    assert first_version != second_version != third_version
    assert koppeltaal.utils.strip_history_from_link(first_version) == \
        koppeltaal.utils.strip_history_from_link(second_version) == \
        koppeltaal.utils.strip_history_from_link(third_version)


def test_send_versioned_focal_resource_patient(connector, patient):
    response = connector.send('CreateOrUpdatePatient', patient)
    first_version = response[0].fhir_link
    assert patient.fhir_link != first_version
    assert patient.fhir_link == \
        koppeltaal.utils.strip_history_from_link(first_version)

    with pytest.raises(koppeltaal.interfaces.OperationOutcomeError) as info:
        # Sending an update to the Patient without a version, now that the
        # server gave it a version, fails.
        connector.send('CreateOrUpdatePatient', patient)

    assert info.value.outcome.issue[0].details == (
        'No version specified for the focal resource, message is rejected.')

    # When we properly update the Patient's version (FHIR link), we can send
    # an update again. And we get the subsequent version for it.
    patient.fhir_link = first_version
    response = connector.send('CreateOrUpdatePatient', patient)
    second_version = response[0].fhir_link
    assert first_version != second_version
    assert koppeltaal.utils.strip_history_from_link(first_version) == \
        koppeltaal.utils.strip_history_from_link(second_version)

    # Reusing the earlier version results in an error.
    patient.fhir_link = first_version
    with pytest.raises(koppeltaal.interfaces.OperationOutcomeError) as info:
        response = connector.send('CreateOrUpdatePatient', patient)

    assert info.value.outcome.issue[0].details == (
        'The specified resource version is not correct')

    patient.fhir_link = second_version
    response = connector.send('CreateOrUpdatePatient', patient)
    third_version = response[0].fhir_link
    assert first_version != second_version != third_version
    assert koppeltaal.utils.strip_history_from_link(first_version) == \
        koppeltaal.utils.strip_history_from_link(second_version) == \
        koppeltaal.utils.strip_history_from_link(third_version)


def test_send_patient_resource_message(connector, patient):
    connector.send('CreateOrUpdatePatient', patient)


def test_send_practitioner_resource_message(connector, practitioner):
    connector.send('CreateOrUpdatePractitioner', practitioner)


def test_send_versioned_focal_resource_related_person(connector,
                                                      related_person):
    response = connector.send('CreateOrUpdateRelatedPerson',
        related_person, related_person.patient)
    first_version = response[0].fhir_link
    assert related_person.fhir_link != first_version
    assert related_person.fhir_link == \
        koppeltaal.utils.strip_history_from_link(first_version)

    with pytest.raises(koppeltaal.interfaces.OperationOutcomeError) as info:
        # Sending an update to the RelatedPerson without a version, now that
        # the server gave it a version, fails.
        connector.send('CreateOrUpdateRelatedPerson',
            related_person, related_person.patient)

    assert info.value.outcome.issue[0].details == (
        'No version specified for the focal resource, message is rejected.')

    # When we properly update the RelatedPerson's version (FHIR link), we
    # can send an update again. And we get the subsequent version for it.
    related_person.fhir_link = first_version
    response = connector.send('CreateOrUpdateRelatedPerson',
        related_person, related_person.patient)
    second_version = response[0].fhir_link
    assert first_version != second_version
    assert koppeltaal.utils.strip_history_from_link(first_version) == \
        koppeltaal.utils.strip_history_from_link(second_version)

    # Reusing the earlier version results in an error.
    related_person.fhir_link = first_version
    with pytest.raises(koppeltaal.interfaces.OperationOutcomeError) as info:
        response = connector.send('CreateOrUpdateRelatedPerson',
            related_person, related_person.patient)

    assert info.value.outcome.issue[0].details == (
        'The specified resource version is not correct')

    related_person.fhir_link = second_version
    response = connector.send('CreateOrUpdateRelatedPerson',
        related_person, related_person.patient)
    third_version = response[0].fhir_link
    assert first_version != second_version != third_version
    assert koppeltaal.utils.strip_history_from_link(first_version) == \
        koppeltaal.utils.strip_history_from_link(second_version) == \
        koppeltaal.utils.strip_history_from_link(third_version)


def test_send_related_person_resource_message(connector, related_person):
    connector.send('CreateOrUpdateRelatedPerson',
        related_person, related_person.patient)


def test_send_related_person_resource_in_careplan(
        connector, careplan, related_person):
    careplan.participants.append(
        koppeltaal.models.Participant(
            member=related_person,
            role='Thirdparty'))
    response = connector.send(
        'CreateOrUpdateCarePlan', careplan, careplan.patient)

    msghdr = [model for model in connector.search(patient=careplan.patient)][0]
    bundle = connector.search(message_id=msghdr.fhir_link)
    for m in bundle:
        if koppeltaal.definitions.RelatedPerson.providedBy(m):
            assert koppeltaal.utils.strip_history_from_link(m.fhir_link) == \
                koppeltaal.utils.strip_history_from_link(
                    related_person.fhir_link)
