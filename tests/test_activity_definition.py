import json
import py.path
import pytest
import zope.interface.verify
import koppeltaal.definitions
import koppeltaal.bundle

here = py.path.local(__file__)


@pytest.fixture
def activity_definition_response():
    return json.load(here.dirpath() / 'fixtures/activity_definition.json')


def test_unpack_activities(activity_definition_response):
    """From the activities json, get a list of activity information objects.
    """
    bundle = koppeltaal.bundle.Bundle()
    bundle.add_response(activity_definition_response)
    activities = list(bundle.unpack())

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
