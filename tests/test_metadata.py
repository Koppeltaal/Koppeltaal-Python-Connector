import py.path


def test_request_metadata(connector):
    result = connector.metadata()
    assert result.startswith('<Conformance')


def test_request_metadata_public_access(connector, monkeypatch):
    # Patch the password to test this.
    monkeypatch.setattr(connector, 'password', 'foobar')
    assert connector.password == 'foobar'
    result = connector.metadata()
    assert result.startswith('<Conformance')


def test_parse_metadata():
    from koppeltaal.metadata import metadata

    here = py.path.local(__file__)
    sample_metadata = (here.dirpath() / 'fixtures/sample_metadata.xml').read()

    parsed = metadata(sample_metadata)
    assert parsed == {
        'messaging': {
            'endpoint':
                'https://testconnectors.vhscloud.nl/FHIR/Koppeltaal/Mailbox'
        }}
