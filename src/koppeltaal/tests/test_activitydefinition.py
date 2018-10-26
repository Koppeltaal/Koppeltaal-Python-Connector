# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import zope.interface.verify
import koppeltaal.definitions
import koppeltaal.interfaces
import koppeltaal.models
import koppeltaal.testing


def test_activities_from_fixture(connector, transport):
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/Other/_search?code=ActivityDefinition',
        respond_with='fixtures/activities_game.json')

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
        'GET',
        '/FHIR/Koppeltaal/Other/_search?code=ActivityDefinition',
        respond_with='fixtures/activities_game.json')
    transport.expect(
        'GET',
        '/FHIR/Koppeltaal/Other/_search?code=ActivityDefinition',
        respond_with='fixtures/activities_game.json')

    activity = connector.activity('FOO')
    assert activity is None

    activity = connector.activity('KTSTESTGAME')
    assert activity is not None
    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.ActivityDefinition, activity)
    assert activity.identifier == 'KTSTESTGAME'
    assert activity.name == 'Test game'
    assert activity.kind == 'Game'


def test_createorupdate_activitydefinition(connector, transport):
    transport.expect(
        'POST',
        '/FHIR/Koppeltaal/Mailbox',
        respond_with='fixtures/bundle_post_activitydefinition_ok.json')

    definition = koppeltaal.models.ActivityDefinition(
        application=koppeltaal.models.ReferredResource(display='Foobar'),
        description=u'A First Activity Definition',
        identifier=u'foobar',
        kind='ELearning',
        name=u'AD-1',
        performer='Patient',
        subactivities=[])

    response_data = connector.send(
        'CreateOrUpdateActivityDefinition', definition)
    assert len(response_data) == 1
    assert zope.interface.verify.verifyObject(
        koppeltaal.interfaces.IReferredFHIRResource, response_data[0])
    assert response_data[0].fhir_link == (
        'https://example.com/fhir/Koppeltaal/ActivityDefinition/1/'
        '_history/1970-01-01T01:01:01:01.1')

    response = transport.called.get('/FHIR/Koppeltaal/Mailbox')
    assert response is not None


def test_create_activitydefinition(connector, transport):
    transport.expect(
        'POST',
        koppeltaal.interfaces.OTHER_URL,
        redirect_to=(
            'https://example.com/fhir/Koppeltaal/ActivityDefinition/1/'
            '_history/1970-01-01T01:01:01:01.1'))

    definition = koppeltaal.models.ActivityDefinition(
        application=koppeltaal.models.ReferredResource(display='Foobar'),
        description=u'A First Activity Definition',
        identifier=u'foobar',
        kind='ELearning',
        name=u'AD-1',
        performer='Patient',
        subactivities=[])

    definition = connector.send_activity(definition)
    assert definition.fhir_link == (
        'https://example.com/fhir/Koppeltaal/ActivityDefinition/1/'
        '_history/1970-01-01T01:01:01:01.1')


def test_update_activitydefinition(connector, transport):
    transport.expect(
        'PUT',
        '/fhir/Koppeltaal/ActivityDefinition/1/'
        '_history/1970-01-01T01:01:01:01.1',
        redirect_to=(
            'https://example.com/fhir/Koppeltaal/ActivityDefinition/1/'
            '_history/1970-02-02T02:02:02:02.2'))

    definition = koppeltaal.models.ActivityDefinition(
        application=koppeltaal.models.ReferredResource(display='Foobar'),
        description=u'A First Activity Definition',
        identifier=u'foobar',
        kind='ELearning',
        name=u'AD-1',
        performer='Patient',
        subactivities=[])
    definition.fhir_link = (
        'https://example.com/fhir/Koppeltaal/ActivityDefinition/1/'
        '_history/1970-01-01T01:01:01:01.1')

    definition = connector.send_activity(definition)
    assert definition.fhir_link == (
        'https://example.com/fhir/Koppeltaal/ActivityDefinition/1/'
        '_history/1970-02-02T02:02:02:02.2')
