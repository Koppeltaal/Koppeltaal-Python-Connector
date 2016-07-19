import ConfigParser
import datetime
import os.path
import pytest
import urlparse
import uuid
import selenium.webdriver
import koppeltaal.connector
import koppeltaal.models
import koppeltaal.testing


def pytest_addoption(parser):
    '''Add server URL to be passed in.'''
    parser.addoption(
        '--server',
        help='Koppeltaal server URL',
        default="https://edgekoppeltaal.vhscloud.nl")


@pytest.fixture(scope='session')
def connector(request):
    # Get the password from the ~/.koppeltaal.cfg
    local_config = os.path.expanduser('~/.koppeltaal.cfg')
    if not os.path.isfile(local_config):
        raise ValueError("Can't find ~/.koppeltaal.cfg")

    server = request.config.option.server
    if not server:
        raise ValueError("No server defined.")

    parsed = urlparse.urlparse(server)
    if parsed.scheme != 'https' or \
            parsed.netloc == '' or \
            parsed.path != '' or \
            parsed.params != '' or \
            parsed.query != '' or \
            parsed.fragment != '':
        raise ValueError('Incorrect server URL')

    config = ConfigParser.ConfigParser()
    config.read(local_config)

    if not config.has_section(server):
        raise ValueError("Can't find {} in ~/.koppeltaal.cfg".format(server))

    username = config.get(server, 'username')
    password = config.get(server, 'password')
    domain = config.get(server, 'domain')

    configuration = koppeltaal.connector.FHIRConfiguration(
        name='Python connector tests')
    return koppeltaal.connector.Connector(
        server, username, password, domain, configuration)


@pytest.fixture
def transport(monkeypatch, connector):
    transport = koppeltaal.testing.MockTransport('koppeltaal.tests')
    monkeypatch.setattr(connector, 'transport', transport)
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
def testgame_definition(connector):
    # Highly depending on what's activated on the server.
    definition = connector.activity('KTSTESTGAME')
    assert definition is not None, 'Test activity not found.'
    return definition


@pytest.fixture
def careplan(patient, practitioner, testgame_definition):
    participants = [koppeltaal.models.Participant(
        member=practitioner,
        role='Caregiver')]
    return koppeltaal.models.CarePlan(
        activities=[koppeltaal.models.Activity(
            identifier=unicode(uuid.uuid4()),
            definition=testgame_definition.identifier,
            kind=testgame_definition.kind,
            participants=participants,
            planned=datetime.datetime.now(),
            status='Available')],
        patient=patient,
        participants=participants,
        status='active')


@pytest.fixture
def careplan_sent(connector, careplan):
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
