import zope.interface.verify
import koppeltaal.interfaces


def test_connector(connector):
    assert koppeltaal.interfaces.IConnector.providedBy(connector)
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IConnector, connector)
