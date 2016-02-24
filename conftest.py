import uuid
import urlparse
import pytest
import os.path
import ConfigParser
import selenium.webdriver
import koppeltaal.connect
import koppeltaal.model
import koppeltaal.feed


def pytest_addoption(parser):
    '''Add server URL to be passed in.'''
    parser.addoption('--server', help='Koppeltaal server URL')


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

    connector = koppeltaal.connect.Connector(
        server, username, password, domain=domain)

    # Test username+password.
    if not connector.test_authentication():
        raise ValueError('Wrong username/password/server combination.')
    return connector


def random_id():
    # Max 36 chars.
    return 'py-{}'.format(str(uuid.uuid4()).replace('-', ''))


@pytest.fixture
def patient(request, connector):
    id = random_id()
    p = koppeltaal.model.Patient(
        id, 'http://example.com/patient/{}'.format(id))
    p.name.given = 'Claes'
    p.name.family = 'de Vries'

    def cleanup_patient_messages():
        result = connector.messages(patient=p)
        for message in koppeltaal.feed.parse(result):
            connector.message_process(message.id, action='success')

    request.addfinalizer(cleanup_patient_messages)
    return p


@pytest.fixture
def practitioner():
    id = random_id()
    p = koppeltaal.model.Practitioner(
        id, 'http://example.com/practitioner/{}'.format(id))
    p.name.given = 'Jozef'
    p.name.family = 'van Buuren'
    return p


@pytest.fixture
def practitioner2():
    id = random_id()
    p = koppeltaal.model.Practitioner(
        id, 'http://example.com/practitioner/{}'.format(id))
    p.name.given = 'Hank'
    p.name.family = 'Schrader'
    return p


@pytest.fixture
def careplan(connector, patient):
    id = random_id()
    return koppeltaal.model.CarePlan(
        id,
        'http://example.com/patient/{p.id}/careplan/{id}'.format(
            id=id,
            p=patient),
        patient
    )


@pytest.fixture
def activity(connector):
    from koppeltaal.activity_definition import parse
    # Highly depending on what's activated on the server.
    for activity in parse(connector.activity_definition()):
        if activity.kind['code'] == 'Game':
            return activity
        else:
            continue
    else:
        raise ValueError('No activity found.')


@pytest.fixture
def careplan_on_server(
        connector, activity, patient, practitioner, careplan):
    from koppeltaal.create_or_update_care_plan import generate

    xml = generate(connector.domain, activity, careplan, practitioner)
    connector.post_message(xml)
    return careplan


@pytest.fixture(scope='session')
def driver(request):
    d = selenium.webdriver.Firefox()
    request.addfinalizer(d.quit)
    return d

@pytest.fixture
def browser(driver, request):
    request.addfinalizer(driver.delete_all_cookies)
    return driver
