# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import pytest
import hamcrest
import zope.interface.verify
import koppeltaal.definitions
import koppeltaal.interfaces
import koppeltaal.testing


def test_connector(connector):
    assert koppeltaal.interfaces.IConnector.providedBy(connector)
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IConnector, connector)


def test_search_message_id_from_fixture(connector, transport):
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?_id=45909',
        respond_with='fixtures/bundle_one_message.json')

    models = list(connector.search(message_id='45909'))
    assert len(models) > 1

    message = models[0]
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.MessageHeader, message)
    assert message.event == 'CreateOrUpdateCarePlan'
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.CarePlan, message.data[0])
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.Patient, message.patient)


def test_send_careplan_success_from_fixture(
        connector, transport, careplan_from_fixture):
    transport.expect(
        'POST',
        '/FHIR/Koppeltaal/Mailbox',
        respond_with='fixtures/bundle_post_careplan_ok.json')
    response_data = connector.send(
        'CreateOrUpdateCarePlan',
        careplan_from_fixture,
        careplan_from_fixture.patient)
    assert len(response_data) == 3
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IReferredFHIRResource, response_data[0])
    assert response_data[0].fhir_link == (
        'https://example.com/fhir/Koppeltaal/CarePlan/1/'
        '_history/1970-01-01T01:01:01:01.1')
    assert response_data[1].fhir_link == (
        'https://example.com/fhir/Koppeltaal/Practitioner/1/'
        '_history/1970-01-01T01:01:01:01.1')
    assert response_data[2].fhir_link == (
        'https://example.com/fhir/Koppeltaal/Patient/1/'
        '_history/1970-01-01T01:01:01:01.1')

    response = transport.called.get('/FHIR/Koppeltaal/Mailbox')
    assert response is not None


def test_send_careplan_success_from_fixture_versioned_focal_resource(
        connector, transport, careplan_from_fixture):
    transport.expect(
        'POST',
        '/FHIR/Koppeltaal/Mailbox',
        respond_with='fixtures/bundle_post_careplan_ok.json')
    response_data = connector.send(
        'CreateOrUpdateCarePlan',
        careplan_from_fixture,
        careplan_from_fixture.patient)
    assert len(response_data) == 3
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IReferredFHIRResource, response_data[0])
    assert response_data[0].fhir_link == (
        'https://example.com/fhir/Koppeltaal/CarePlan/1/'
        '_history/1970-01-01T01:01:01:01.1')
    assert response_data[1].fhir_link == (
        'https://example.com/fhir/Koppeltaal/Practitioner/1/'
        '_history/1970-01-01T01:01:01:01.1')
    assert response_data[2].fhir_link == (
        'https://example.com/fhir/Koppeltaal/Patient/1/'
        '_history/1970-01-01T01:01:01:01.1')

    response = transport.called.get('/FHIR/Koppeltaal/Mailbox')
    assert response is not None


def test_send_careplan_fail_message_response_error_fixture(
        connector, transport, careplan_from_fixture):
    transport.expect(
        'POST',
        '/FHIR/Koppeltaal/Mailbox',
        respond_with='fixtures/bundle_post_careplan_failed.json')
    with pytest.raises(koppeltaal.interfaces.MessageResponseError) as cm:
        connector.send(
            'CreateOrUpdateCarePlan',
            careplan_from_fixture,
            careplan_from_fixture.patient)

    response = transport.called.get('/FHIR/Koppeltaal/Mailbox')
    assert response is not None
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.MessageHeader,
        cm.value.message)
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.MessageHeaderResponse,
        cm.value.message.response)


def test_send_careplan_operation_outcome_error_from_fixture(
        connector, transport, careplan_from_fixture):
    transport.expect(
        'POST',
        '/FHIR/Koppeltaal/Mailbox',
        respond_error='fixtures/operation_outcome.json')
    with pytest.raises(koppeltaal.interfaces.OperationOutcomeError) as cm:
        connector.send(
            'CreateOrUpdateCarePlan',
            careplan_from_fixture,
            careplan_from_fixture.patient)

    response = transport.called.get('/FHIR/Koppeltaal/Mailbox')
    assert response is not None
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.OperationOutcome,
        cm.value.outcome)
    assert len(cm.value.outcome.issue) == 2
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.Issue,
        cm.value.outcome.issue[0])
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IReferredFHIRResource,
        cm.value.outcome.issue[0].resource)
    assert cm.value.outcome.issue[0].resource.fhir_link == \
        'https://example.com/fhir/Koppeltaal/Patient/1'
    assert cm.value.outcome.issue[0].details == (
        'Message Version mismatch: Please retrieve the latest version of '
        'this Message and apply changes before resubmit.')
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.Issue,
        cm.value.outcome.issue[1])
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IReferredFHIRResource,
        cm.value.outcome.issue[1].resource)
    assert cm.value.outcome.issue[1].resource.fhir_link == \
        'https://example.com/fhir/Koppeltaal/Practitioner/1'
    assert cm.value.outcome.issue[1].details == (
        'Message Version mismatch: Please retrieve the latest version of '
        'this Message and apply changes before resubmit.')


def test_updates_implicit_success_from_fixture(connector, transport):
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_one_message.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_zero_messages.json')
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

    updates = list(connector.updates())
    assert len(updates) == 1
    for update in updates:
        with update:
            assert zope.interface.verify.verifyObject(
                koppeltaal.interfaces.IUpdate, update)
            assert zope.interface.verify.verifyObject(
                koppeltaal.definitions.MessageHeader, update.message)
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
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_one_message.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_zero_messages.json')
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

    updates = list(connector.updates())
    assert len(updates) == 1
    for update in updates:
        with update:
            assert zope.interface.verify.verifyObject(
                koppeltaal.interfaces.IUpdate, update)
            assert zope.interface.verify.verifyObject(
                koppeltaal.definitions.MessageHeader, update.message)
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
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_one_message.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_zero_messages.json')
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

    updates = list(connector.updates())
    assert len(updates) == 1
    for update in updates:
        with update:
            assert zope.interface.verify.verifyObject(
                koppeltaal.interfaces.IUpdate, update)
            assert zope.interface.verify.verifyObject(
                koppeltaal.definitions.MessageHeader, update.message)
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
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_one_message.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_zero_messages.json')
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

    updates = list(connector.updates())
    assert len(updates) == 1
    with pytest.raises(ValueError):
        for update in updates:
            with update:
                assert zope.interface.verify.verifyObject(
                    koppeltaal.interfaces.IUpdate, update)
                assert zope.interface.verify.verifyObject(
                    koppeltaal.definitions.MessageHeader, update.message)
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
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_one_message.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_zero_messages.json')
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

    updates = list(connector.updates())
    assert len(updates) == 1
    with pytest.raises(ValueError):
        for update in updates:
            with update:
                assert zope.interface.verify.verifyObject(
                    koppeltaal.interfaces.IUpdate, update)
                assert zope.interface.verify.verifyObject(
                    koppeltaal.definitions.MessageHeader, update.message)
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
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_one_error.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_zero_messages.json')
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

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


def test_updates_expected_event(connector, transport):
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_one_message.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_zero_messages.json')
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

    updates = list(connector.updates(
        expected_events=['CreateOrUpdateCarePlan']))
    assert len(updates) == 1
    for update in updates:
        with update:
            assert update.message.event == 'CreateOrUpdateCarePlan'

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


def test_updates_unexpected_event(connector, transport):
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_one_message.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_zero_messages.json')
    # This is the response from the KT server after sending the fail.
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

    # We ask for updates but only allow CreateOrUpdatePatient events. Since
    # the message we'll retrieve is a CreateOrUpdateCarePlan, we should see
    # that the message is acknowledged as "fail".
    updates = list(connector.updates(
        expected_events=['CreateOrUpdatePatient']))
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
                    hamcrest.has_entry('valueString', "Event not expected"))
            )))


def test_updates_for_patient(connector, transport):
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim&'
        'Patient=https%3A%2F%2Fapp.minddistrict.com%2Ffhir%2FKoppeltaal'
        '%2FPatient%2F1394433515',
        respond_with='fixtures/bundle_one_message.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim&'
        'Patient=https%3A%2F%2Fapp.minddistrict.com%2Ffhir%2FKoppeltaal'
        '%2FPatient%2F1394433515',
        respond_with='fixtures/bundle_zero_messages.json')
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

    updates = list(connector.updates(patient=(
        'https://app.minddistrict.com/fhir/Koppeltaal/Patient/1394433515')))
    assert len(updates) == 1
    for update in updates:
        with update:
            assert update.message.event == 'CreateOrUpdateCarePlan'

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


def test_updates_for_event(connector, transport):
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim&event=CarePlan',
        respond_with='fixtures/bundle_one_message.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim&event=CarePlan',
        respond_with='fixtures/bundle_zero_messages.json')
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

    updates = list(connector.updates(event='CarePlan'))
    assert len(updates) == 1
    for update in updates:
        with update:
            assert update.message.event == 'CreateOrUpdateCarePlan'

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


def test_updates_unexpected_event_no_events_at_all(connector, transport):
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_one_message.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_zero_messages.json')
    # This is the response from the KT server after sending the fail.
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

    # We ask for updates but do not allow any events. Since the message we'll
    # retrieve is a CreateOrUpdateCarePlan, we should see that the message is
    # acknowledged as "fail".
    updates = list(connector.updates(expected_events=[]))
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
                    hamcrest.has_entry('valueString', "Event not expected"))
            )))


def test_updates_same_source_acked(connector, transport):
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_one_message_same_source.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/MessageHeader/_search?'
        '_query=MessageHeader.GetNextNewAndClaim',
        respond_with='fixtures/bundle_zero_messages.json')
    transport.expect(
        'PUT',
        '/FHIR/Koppeltaal/MessageHeader/45909'
        '/_history/2016-07-15T11:50:24:494.7839',
        respond_with='fixtures/resource_put_message.json')

    # The one incoming messages is from our "own" endpoint. This is not a
    # message we will process, but it is "acked" as success.

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
            koppeltaal.testing.has_extension(
                '#ProcessingStatusStatus',
                hamcrest.has_entry('valueCode', 'Success'))))
