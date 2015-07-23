import py.path
import pytest
from koppeltaal import KoppeltaalException
from koppeltaal.activity_definition import activity_info, parse

here = py.path.local(__file__)
sample_feed = (here.dirpath() / 'fixtures/sample_activity_definition.xml').read()


def test_parse_activities():
    '''
    From the activities feed, get a list of activity information objects.
    '''
    activity_infos = list(parse(sample_feed))
    assert len(activity_infos) == 3
    ad1 = activity_infos[0]
    assert ad1.node is not None
    assert ad1.id == 'AD1'
    assert ad1.name == 'Game AD1'

    ad3 = activity_infos[2]
    assert ad3.id == 'AD3'


def test_activity_info():
    '''
    From the activities feed, find the activity with the activity id.
    '''
    ad2 = activity_info(sample_feed, 'AD2')
    assert ad2.id == 'AD2'

    assert ad2.kind == {
        'code': 'Game',
        'display': 'Game'}

    with pytest.raises(KoppeltaalException):
        activity_info(sample_feed, 'unknown')


def test_request_activity_definition(connector):
    '''Some smoke tests to test URL and authentication.'''
    result = connector.activity_definition()
    assert result.startswith('<feed')
    assert 'ActivityDefinition' in result
