import uuid
import urlparse
import pytest
import os.path
import ConfigParser
import selenium.webdriver
import koppeltaal.configuration
import koppeltaal.connector
import koppeltaal.models


try:
    import zope.component

    class URLAdapter(object):
        def __init__(self, context):
            self.context = context

        def url(self, *args, **kw):
            version = getattr(self.context, '__version__', None)
            if version is not None:
                return version

            return 'https://example.com/{}/{}'.format(
                self.context.__class__.__name__.lower(),
                koppeltaal.identity(self.context))

    class IDAdapter(object):
        def __init__(self, context):
            self.context = context

        def id(self, *args, **kw):
            id = getattr(self.context, '__identity__', None)
            if id is None:
                id = self.context.__identity__ = str(uuid.uuid4())
            return id

    zope.component.provideAdapter(
        URLAdapter,
        adapts=(zope.interface.Interface,),
        provides=koppeltaal.interfaces.IURL)

    zope.component.provideAdapter(
        IDAdapter,
        adapts=(zope.interface.Interface,),
        provides=koppeltaal.interfaces.IID)

except ImportError:
    @pytest.fixture(scope='session', autouse=True)
    def _config_url():
        """URL function in the context of the test runs."""

        def url_function(context):
            version = getattr(context, '__version__', None)
            if version is not None:
                return version

            return 'https://example.com/{}/{}'.format(
                context.__class__.__name__.lower(),
                koppeltaal.identity(context))

        koppeltaal.configuration.set_url_function(url_function)

    @pytest.fixture(scope='session', autouse=True)
    def _config_identity():
        """Identity function in the context of the test runs."""

        def identity_function(context):
            # We cannot use id(context) as that id might be reused for objects
            # that have a non-overlapping life-cycle. We store a identity on
            # the object and reuse that one.
            id = getattr(context, '__identity__', None)
            if id is None:
                id = context.__identity__ = str(uuid.uuid4())
            return id

        koppeltaal.configuration.set_identity_function(identity_function)


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

    return koppeltaal.connector.Connector(
        server, username, password, domain=domain)


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
