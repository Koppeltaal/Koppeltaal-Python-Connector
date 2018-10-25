# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import hamcrest
import zope.interface.verify
import koppeltaal.definitions
import koppeltaal.interfaces
import koppeltaal.testing


def test_recieve_careteam(connector, transport):
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
            assert update.message.event == 'CreateOrUpdateCarePlan'
            careplan = update.data
            patient = update.patient
            assert zope.interface.verify.verifyObject(
                koppeltaal.definitions.CarePlan, update.data)

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

    assert len(careplan.participants) == 3
    for participant in careplan.participants:
        assert zope.interface.verify.verifyObject(
            koppeltaal.definitions.Participant, participant)
        assert len(participant.careteam) == 2
        assert participant.careteam[0].name == 'The Therapists Team'
        assert participant.careteam[1].name == 'The Supervisors Team'
        assert participant.careteam[0].subject is patient
