import hamcrest
import koppeltaal.definitions
import koppeltaal.interfaces
import koppeltaal.testing
import zope.interface.verify


def test_connector(connector):
    assert koppeltaal.interfaces.IConnector.providedBy(connector)
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IConnector, connector)


def test_activities_from_fixture(connector, transport):
    transport.expect_json(
        '/FHIR/Koppeltaal/Other/_search?code=ActivityDefinition',
        ['fixtures/activities_game.json'])

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


def test_activity_from_fixture(connector, transport):
    transport.expect_json(
        '/FHIR/Koppeltaal/Other/_search?code=ActivityDefinition',
        ['fixtures/activities_game.json',
         'fixtures/activities_game.json'])

    activity = connector.activity('FOO')
    assert activity is None

    activity = connector.activity('KTSTESTGAME')
    assert activity is not None
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.ActivityDefinition, activity)
    assert activity.identifier == 'KTSTESTGAME'
    assert activity.name == 'Test game'
    assert activity.kind == 'Game'


def test_search_message_id_from_fixture(connector, transport):
    transport.expect_json(
        '/FHIR/Koppeltaal/MessageHeader/_search?_id=45909',
        ['fixtures/bundle_one_message.json'])

    models = list(connector.search(message_id='45909'))
    assert len(models) > 1

    message = models[0]
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.MessageHeader, message)
    assert message.event == 'CreateOrUpdateCarePlan'
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.CarePlan, message.data)
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.Patient, message.patient)


def test_updates_success_from_fixture(connector, transport):
    transport.expect_json(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        ['fixtures/bundle_one_message.json',
         'fixtures/bundle_zero_messages.json'])
    transport.expect_json(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        ['fixtures/message_header_ok.json'])

    updates = list(connector.updates())
    assert len(updates) == 1
    for update in updates:
        with update:
            assert zope.interface.verify.verifyObject(
                koppeltaal.definitions.CarePlan, update.data)
            assert zope.interface.verify.verifyObject(
                koppeltaal.definitions.Patient, update.patient)

    response = transport.called.get(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839')
    assert response is not None
    hamcrest.assert_that(
        response,
        hamcrest.has_entry(
            'extension',
            hamcrest.has_item(
                hamcrest.has_entry(
                    'extension',
                    hamcrest.has_item(
                        hamcrest.has_entries({
                            'url': hamcrest.ends_with(
                                '#ProcessingStatusStatus'),
                            'valueCode': 'Success'
                        }))))),
        'message set to success')


def test_updates_error_from_fixture(connector, transport):
    transport.expect_json(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        ['fixtures/bundle_one_error.json',
         'fixtures/bundle_zero_messages.json'])
    transport.expect_json(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        ['fixtures/message_header_ok.json'])

    updates = list(connector.updates())
    assert len(updates) == 0

    response = transport.called.get(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839')
    assert response is not None
    hamcrest.assert_that(
        response,
        hamcrest.has_entry(
            'extension',
            hamcrest.has_item(
                hamcrest.has_entry(
                    'extension',
                    hamcrest.has_items(
                        hamcrest.has_entries({
                            'url': hamcrest.ends_with(
                                '#ProcessingStatusStatus'),
                            'valueCode': 'Failed'
                        }),
                        hamcrest.has_entries({
                            'url': hamcrest.ends_with(
                                '#ProcessingStatusException'),
                            'valueString': hamcrest.ends_with(
                                "RequiredMissing: 'startDate' "
                                "required but missing.")
                        })
                    )))),
        'message set to success')
