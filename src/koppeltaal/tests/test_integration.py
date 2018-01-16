# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import koppeltaal.utils
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
