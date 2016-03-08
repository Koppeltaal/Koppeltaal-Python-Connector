import uuid
import urlparse
import pytest
import os.path
import ConfigParser
import selenium.webdriver
import koppeltaal.configuration
import koppeltaal.connect
import koppeltaal.feed
import koppeltaal.model


def pytest_addoption(parser):
    '''Add server URL to be passed in.'''
    parser.addoption('--server', help='Koppeltaal server URL')


@pytest.fixture(scope='session', autouse=True)
def _config_identity():
    """Identity function in the context of the test runs."""

    def identity_function(context):
        # We cannot use id(context) as that id might be reused for objects
        # that have a non-overlapping life-cycle. We store a identity on the
        # object and reuse that one.
        id = getattr(context, '__identity__', None)
        if id is None:
            id = context.__identity__ = str(uuid.uuid4())
        return id

    koppeltaal.configuration.set_identity_function(identity_function)


@pytest.fixture(scope='session', autouse=True)
def _config_url():
    """URL function in the context of the test runs."""

    def url_function(context):
        version = getattr(context, '__version__', None)
        if version is not None:
            return version

        return 'https://example.com/{}/{}'.format(
            context.__class__.__name__.lower(), koppeltaal.identity(context))

    koppeltaal.configuration.set_url_function(url_function)


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


@pytest.fixture
def patient(request, connector):
    p = koppeltaal.model.Patient()
    p.name.given = 'Claes'
    p.name.family = 'de Vries'

    def cleanup_patient_messages():
        result = connector.messages(patient=p)
        for message in koppeltaal.feed.parse(result):
            connector.success(message.__version__)

    request.addfinalizer(cleanup_patient_messages)
    return p


@pytest.fixture
def practitioner():
    p = koppeltaal.model.Practitioner()
    p.name.given = 'Jozef'
    p.name.family = 'van Buuren'
    return p


@pytest.fixture
def practitioner2():
    p = koppeltaal.model.Practitioner()
    p.name.given = 'Hank'
    p.name.family = 'Schrader'
    return p


@pytest.fixture
def careplan(connector, patient):
    return koppeltaal.model.CarePlan(patient)


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
