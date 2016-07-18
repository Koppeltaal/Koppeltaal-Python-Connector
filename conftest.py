import urlparse
import pytest
import os.path
import ConfigParser
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
    p = koppeltaal.models.Patient()

    def cleanup_patient_messages():
        # XXX Fix the URL
        for message in connector.messages(patient='fakeurl'):
            message.status = 'Success'
            connector.send(message)

    request.addfinalizer(cleanup_patient_messages)
    return p


@pytest.fixture
def practitioner():
    p = koppeltaal.models.Practitioner()
    p.name = koppeltaal.models.Name()
    p.name.given = 'Jozef'
    p.name.family = 'van Buuren'
    return p


@pytest.fixture
def practitioner2():
    p = koppeltaal.models.Practitioner()
    p.name = koppeltaal.models.Name()
    p.name.given = 'Hank'
    p.name.family = 'Schrader'
    return p


@pytest.fixture
def careplan(connector, patient):
    return koppeltaal.model.CarePlan(patient)


@pytest.fixture
def activities(connector):
    return connector.activities()


@pytest.fixture(scope='session')
def driver(request):
    d = selenium.webdriver.Firefox()
    request.addfinalizer(d.quit)
    return d


@pytest.fixture
def browser(driver, request):
    request.addfinalizer(driver.delete_all_cookies)
    return driver
