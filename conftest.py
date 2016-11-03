import datetime
import pytest
import uuid
import selenium.webdriver
import koppeltaal.connector
import koppeltaal.models
import koppeltaal.testing
import koppeltaal.utils


def pytest_addoption(parser):
    '''Add server URL to be passed in.'''
    parser.addoption(
        '--server',
        help='Koppeltaal server URL',
        default="https://edgekoppeltaal.vhscloud.nl")


@pytest.fixture(scope='session')
def connector(request):
    server = request.config.option.server
    if not server:
        raise ValueError("No server name defined.")
    credentials = koppeltaal.utils.get_credentials_from_file(server)
    integration = koppeltaal.connector.Integration(
        name='Python connector tests')
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
        name=koppeltaal.models.Name(
            family=u"Doe",
            given=u"John"),
        age=42,
        gender="M",
        active=True)

    # def cleanup_patient_messages():
    #     # XXX Fix the URL
    #     for message in connector.search(patient='fakeurl'):
    #         message.status = 'Success'
    #         connector.send(message)

    # request.addfinalizer(cleanup_patient_messages)
    return patient


@pytest.fixture
def practitioner():
    return koppeltaal.models.Practitioner(
        name=koppeltaal.models.Name(
            given=u'John',
            family=u'Q. Practitioner'))


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
    return request.getfuncargvalue('careplan')


@pytest.fixture
def careplan_response(connector, careplan):
    return connector.send(
        'CreateOrUpdateCarePlan', careplan, careplan.patient)


@pytest.fixture(scope='session')
def driver(request):
    driver = selenium.webdriver.Firefox()
    request.addfinalizer(driver.quit)
    return driver


@pytest.fixture
def browser(driver, request):
    request.addfinalizer(driver.delete_all_cookies)
    return driver
