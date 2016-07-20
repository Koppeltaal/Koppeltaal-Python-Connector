import hamcrest
import pytest
import koppeltaal.definitions
import koppeltaal.interfaces
import koppeltaal.testing
import zope.interface.verify


def test_connector(connector):
    assert koppeltaal.interfaces.IConnector.providedBy(connector)
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IConnector, connector)


def test_activities_from_fixture(connector, transport):
    transport.expect(
        '/FHIR/Koppeltaal/Other/_search?code=ActivityDefinition',
        json='fixtures/activities_game.json')

    activities = list(connector.activities())
    assert len(activities) == 2

    activity1, activity2 = activities

    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.ActivityDefinition, activity1)
    assert activity1.identifier == 'KTSTESTGAME'
    assert activity1.name == 'Test game'
    assert activity1.kind == 'Game'
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IReferredFHIRResource, activity1.application)

    assert activity1.description == 'Testtest'
    assert activity1.fhir_link == (
        'https://edgekoppeltaal.vhscloud.nl/FHIR/Koppeltaal/Other/'
        'ActivityDefinition:3/_history/2016-07-04T07:49:01:742.1933')
    assert activity1.is_active is False
    assert activity1.is_archived is False
    assert activity1.is_domain_specific is False
    assert activity1.launch_type == 'Web'
    assert activity1.performer == 'Patient'
    assert activity1.subactivities == []

    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.ActivityDefinition, activity2)
    assert activity2.identifier == 'RANJKA'
    assert activity2.name == 'Ranj Kick ASS Game'
    assert activity2.kind == 'Game'

    assert activity2.description is None
    assert activity2.fhir_link == (
        'https://edgekoppeltaal.vhscloud.nl/FHIR/Koppeltaal/Other/'
        'ActivityDefinition:1433/_history/2016-07-04T09:04:24:679.3465')
    assert activity2.is_active is True
    assert activity2.is_archived is False
    assert activity2.is_domain_specific is True
    assert activity2.launch_type == u'Web'
    assert activity2.performer == u'Patient'
    assert len(activity2.subactivities) == 12
    for subactivity in activity2.subactivities:
        assert zope.interface.verify.verifyObject(
            koppeltaal.definitions.SubActivityDefinition, subactivity)

    assert subactivity.active is False
    assert subactivity.description == (
        u"Het is vrijdagmiddag en de werkweek is bijna voorbij. Maar niet "
        "voor jou, want jij moet voor vijf uur handgeschreven notulen "
        "hebben uitgewerkt. Je collega's treffen ondertussen de "
        "voorbereidingen voor het vieren van de verjaardag van hun chef.")
    assert subactivity.identifier == u'scenario_12'
    assert subactivity.name == u'Verjaardag op het werk'


def test_activity_from_fixture(connector, transport):
    transport.expect(
        '/FHIR/Koppeltaal/Other/_search?code=ActivityDefinition',
        json='fixtures/activities_game.json')
    transport.expect(
        '/FHIR/Koppeltaal/Other/_search?code=ActivityDefinition',
        json='fixtures/activities_game.json')

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
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?_id=45909',
        json='fixtures/bundle_one_message.json')

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


def test_send_careplan_success_from_fixture(
        connector, transport, careplan_from_fixture):
    transport.expect(
        '/FHIR/Koppeltaal/Mailbox',
        json='fixtures/bundle_post_answer_ok.json')
    message = connector.send(
        'CreateOrUpdateCarePlan',
        careplan_from_fixture,
        careplan_from_fixture.patient)
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IReferredFHIRResource, message)
    assert message.fhir_link == (
        'https://example.com/fhir/Koppeltaal/CarePlan/1/'
        '_history/1970-01-01T01:01:01:01.1')

    response = transport.called.get('/FHIR/Koppeltaal/Mailbox')
    assert response is not None


def test_send_careplan_fail_from_fixture(
        connector, transport, careplan_from_fixture):
    transport.expect(
        '/FHIR/Koppeltaal/Mailbox',
        json='fixtures/bundle_post_answer_failed.json')
    with pytest.raises(koppeltaal.interfaces.InvalidResponse):
        connector.send(
            'CreateOrUpdateCarePlan',
            careplan_from_fixture,
            careplan_from_fixture.patient)

    response = transport.called.get('/FHIR/Koppeltaal/Mailbox')
    assert response is not None


def test_updates_implicit_success_from_fixture(connector, transport):
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_one_message.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_zero_messages.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        json='fixtures/resource_post_message.json')

    updates = list(connector.updates())
    assert len(updates) == 1
    for update in updates:
        with update:
            assert update.message.event == 'CreateOrUpdateCarePlan'
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
        koppeltaal.testing.has_extension(
            '#ProcessingStatus',
            koppeltaal.testing.has_extension(
                '#ProcessingStatusStatus',
                hamcrest.has_entry('valueCode', 'Success'))))


def test_updates_explicit_success_from_fixture(connector, transport):
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_one_message.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_zero_messages.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        json='fixtures/resource_post_message.json')

    updates = list(connector.updates())
    assert len(updates) == 1
    for update in updates:
        with update:
            assert update.message.event == 'CreateOrUpdateCarePlan'
            assert zope.interface.verify.verifyObject(
                koppeltaal.definitions.CarePlan, update.data)
            assert zope.interface.verify.verifyObject(
                koppeltaal.definitions.Patient, update.patient)
            update.success()

    response = transport.called.get(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839')
    assert response is not None
    hamcrest.assert_that(
        response,
        koppeltaal.testing.has_extension(
            '#ProcessingStatus',
            koppeltaal.testing.has_extension(
                '#ProcessingStatusStatus',
                hamcrest.has_entry('valueCode', 'Success'))))


def test_updates_explicit_fail_from_fixture(connector, transport):
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_one_message.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_zero_messages.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        json='fixtures/resource_post_message.json')

    updates = list(connector.updates())
    assert len(updates) == 1
    for update in updates:
        with update:
            assert update.message.event == 'CreateOrUpdateCarePlan'
            assert zope.interface.verify.verifyObject(
                koppeltaal.definitions.CarePlan, update.data)
            assert zope.interface.verify.verifyObject(
                koppeltaal.definitions.Patient, update.patient)
            update.fail("I failed testing it.")

    response = transport.called.get(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839')
    assert response is not None
    hamcrest.assert_that(
        response,
        koppeltaal.testing.has_extension(
            '#ProcessingStatus',
            hamcrest.all_of(
                koppeltaal.testing.has_extension(
                    '#ProcessingStatusStatus',
                    hamcrest.has_entry('valueCode', 'Failed')),
                koppeltaal.testing.has_extension(
                    '#ProcessingStatusException',
                    hamcrest.has_entry('valueString', "I failed testing it."))
            )))


def test_updates_implicit_success_exception_from_fixture(connector, transport):
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_one_message.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_zero_messages.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        json='fixtures/resource_post_message.json')

    updates = list(connector.updates())
    assert len(updates) == 1
    with pytest.raises(ValueError):
        for update in updates:
            with update:
                assert update.message.event == 'CreateOrUpdateCarePlan'
                assert zope.interface.verify.verifyObject(
                    koppeltaal.definitions.CarePlan, update.data)
                assert zope.interface.verify.verifyObject(
                    koppeltaal.definitions.Patient, update.patient)
                raise ValueError("I cannot write code.")

    response = transport.called.get(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839')
    assert response is not None
    hamcrest.assert_that(
        response,
        koppeltaal.testing.has_extension(
            '#ProcessingStatus',
            koppeltaal.testing.has_extension(
                '#ProcessingStatusStatus',
                hamcrest.has_entry('valueCode', 'New'))
            ))


def test_updates_explicit_success_exception_from_fixture(connector, transport):
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_one_message.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_zero_messages.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        json='fixtures/resource_post_message.json')

    updates = list(connector.updates())
    assert len(updates) == 1
    with pytest.raises(ValueError):
        for update in updates:
            with update:
                assert update.message.event == 'CreateOrUpdateCarePlan'
                assert zope.interface.verify.verifyObject(
                    koppeltaal.definitions.CarePlan, update.data)
                assert zope.interface.verify.verifyObject(
                    koppeltaal.definitions.Patient, update.patient)
                update.success()
                raise ValueError("I cannot write code.")

    response = transport.called.get(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839')
    assert response is not None
    hamcrest.assert_that(
        response,
        koppeltaal.testing.has_extension(
            '#ProcessingStatus',
            hamcrest.all_of(
                koppeltaal.testing.has_extension(
                    '#ProcessingStatusStatus',
                    hamcrest.has_entry('valueCode', 'New')),
                hamcrest.not_(
                    koppeltaal.testing.has_extension(
                        '#ProcessingStatusException'))
            )))


def test_updates_error_from_fixture(connector, transport):
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_one_error.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        json='fixtures/bundle_zero_messages.json')
    transport.expect(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        json='fixtures/resource_post_message.json')

    updates = list(connector.updates())
    assert len(updates) == 0

    response = transport.called.get(
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839')
    assert response is not None

    hamcrest.assert_that(
        response,
        koppeltaal.testing.has_extension(
            '#ProcessingStatus',
            hamcrest.all_of(
                koppeltaal.testing.has_extension(
                    '#ProcessingStatusStatus',
                    hamcrest.has_entry('valueCode', 'Failed')),
                koppeltaal.testing.has_extension(
                    '#ProcessingStatusException',
                    hamcrest.has_entry(
                        'valueString',
                        hamcrest.ends_with(
                            "RequiredMissing: 'startDate' "
                            "required but missing.")))
            )))
