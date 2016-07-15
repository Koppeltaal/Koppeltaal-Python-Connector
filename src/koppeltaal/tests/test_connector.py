import koppeltaal.definitions
import koppeltaal.interfaces
import koppeltaal.testing
import zope.interface.verify


def test_connector(connector):
    assert koppeltaal.interfaces.IConnector.providedBy(connector)
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IConnector, connector)


def test_activities_from_fixture(monkeypatch, connector):
    transport = koppeltaal.testing.MockTransport()
    transport.expect_json(
        '/FHIR/Koppeltaal/Other/_search?code=ActivityDefinition',
        'koppeltaal.tests',
        'fixtures/activities_game.json')

    monkeypatch.setattr(connector, 'transport', transport)

    activities = list(connector.activities())
    assert len(activities) == 2

    activity1, activity2 = activities

    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.ActivityDefinition, activity1)
    assert activity1.identifier == 'KTSTESTGAME'
    assert activity1.name == 'Test game'
    assert activity1.kind == 'Game'

    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.ActivityDefinition, activity2)
    assert activity2.identifier == 'RANJKA'
    assert activity2.name == 'Ranj Kick ASS Game'
    assert activity2.kind == 'Game'


def test_activity_from_fixture(monkeypatch, connector):
    transport = koppeltaal.testing.MockTransport()
    transport.expect_json(
        '/FHIR/Koppeltaal/Other/_search?code=ActivityDefinition',
        'koppeltaal.tests',
        'fixtures/activities_game.json')

    monkeypatch.setattr(connector, 'transport', transport)

    activity = connector.activity('FOO')
    assert activity is None

    activity = connector.activity('KTSTESTGAME')
    assert activity is not None
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.ActivityDefinition, activity)
    assert activity.identifier == 'KTSTESTGAME'
    assert activity.name == 'Test game'
    assert activity.kind == 'Game'


def test_search_message_id_from_fixture(monkeypatch, connector):
    transport = koppeltaal.testing.MockTransport()
    transport.expect_json(
        '/FHIR/Koppeltaal/MessageHeader/_search?_id=45909',
        'koppeltaal.tests',
        'fixtures/bundle_one_message.json')

    monkeypatch.setattr(connector, 'transport', transport)

    models = list(connector.search(message_id='45909'))
    assert len(models) > 1

    message = models[0]
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.MessageHeader, message)
    assert message.event == 'CreateOrUpdateCarePlan'
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.CarePlan, message.data)
