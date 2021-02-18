# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import os
import datetime
import uuid
import pytest
import selenium.webdriver
import six
import koppeltaal.interfaces
import koppeltaal.connector
import koppeltaal.models
import koppeltaal.testing
import koppeltaal.utils


unicode = six.text_type


def pytest_addoption(parser):
    '''Add server identifier to be passed in. Looks for corresponding part in
    ~/.koppeltaal.cfg
    '''
    parser.addoption(
        '--server',
        help=("""\
Koppeltaal server identifier. URL and credentials should be
defined in the part identified by that name in ~/.koppeltaal.cfg.

For example:

[edge]
url = https://edgekoppeltaal.vhscloud.nl
domain = PythonAdapterTesting
username = [username]
password = [password]
"""))

    parser.addoption('--baseurl')
    parser.addoption('--domain')
    parser.addoption('--username')
    parser.addoption('--password')


@pytest.fixture(scope='session')
def connector(request):
    server = request.config.option.server
    if server:
        credentials = koppeltaal.utils.get_credentials_from_file(server)
    else:
        credentials = koppeltaal.utils.Credentials(
            os.environ.get('ADAPTER_SERVER'),
            os.environ.get('ADAPTER_USERNAME'),
            os.environ.get('ADAPTER_PASSWORD'),
            os.environ.get('ADAPTER_DOMAIN'),
            {})
    integration = koppeltaal.connector.Integration(
        'Koppeltaal Python Adapter Tests',
        'https://example.com/fhir/Koppeltaal',
        software='Koppeltaal Python Adapter Tests Runner',
        version=koppeltaal.interfaces.VERSION)
    return koppeltaal.connector.Connector(credentials, integration)


@pytest.fixture
def transport(monkeypatch, connector):
    transport = koppeltaal.testing.MockTransport('koppeltaal.tests')
    monkeypatch.setattr(connector, 'transport', transport)
    monkeypatch.setattr(connector.integration, 'model_id', lambda m: u'1')
    monkeypatch.setattr(koppeltaal.utils, 'messageid', lambda: u'1234-5678')
    return transport


@pytest.fixture
def patient(request, connector):
    patient = koppeltaal.models.Patient(
        name=[
            koppeltaal.models.Name(
                family=[u"Doe"],
                given=[u"John"],
                text=u'John Doe')],
        age=42,
        gender="M",
        active=True)
    return patient


@pytest.fixture
def practitioner():
    return koppeltaal.models.Practitioner(
        name=koppeltaal.models.Name(
            given=[u'John'],
            family=[u'Q.', u'Practitioner'],
            text=u'John Q Practitioner'))


@pytest.fixture
def related_person(patient):
    related_person = koppeltaal.models.RelatedPerson(
        patient=patient,
        relationship='PRN',
        name=koppeltaal.models.Name(
                family=[u"Doe"],
                given=[u"John"],
                text=u'John Doe'),
        gender="M",
        address=koppeltaal.models.Address(city='Rotterdam'))
    return related_person


@pytest.fixture
def activity_definition(connector):
    # Highly depending on what's activated on the server.
    definition = connector.activity('KTSTESTGAME')
    assert definition is not None, 'Test activity not found.'
    return definition


@pytest.fixture
def careplan(patient, practitioner, activity_definition):
    participants = [koppeltaal.models.Participant(
        member=practitioner,
        role='Caregiver')]
    return koppeltaal.models.CarePlan(
        activities=[koppeltaal.models.Activity(
            identifier=unicode(uuid.uuid4()),
            definition=activity_definition.identifier,
            kind=activity_definition.kind,
            participants=participants,
            planned=datetime.datetime.now(),
            status='Available')],
        patient=patient,
        participants=participants,
        status='active')


@pytest.fixture
def careplan_from_fixture(request, transport):
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/Other/_search?code=ActivityDefinition',
        respond_with='fixtures/activities_game.json')
    return request.getfixturevalue('careplan')


@pytest.fixture
def careplan_response(connector, careplan):
    return connector.send('CreateOrUpdateCarePlan', careplan, careplan.patient)


@pytest.fixture(scope='session')
def driver(request):
    driver = selenium.webdriver.Firefox()
    request.addfinalizer(driver.quit)
    return driver


@pytest.fixture
def browser(driver, request):
    request.addfinalizer(driver.delete_all_cookies)
    return driver
