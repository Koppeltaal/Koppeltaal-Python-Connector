

def test_request_metadata(connector):
    result = connector.metadata()
    assert isinstance(result, dict)
    assert result.get('name') == 'Koppeltaal'
    assert result.get('version') == 'v1.0'
    assert result.get('fhirVersion') == '0.0.82'
