def test_authentication(connector):
    assert connector.test_authentication()


def test_authentication_wrong_password(connector, monkeypatch):
    monkeypatch.setattr(connector, 'password', 'foobar')
    assert not connector.test_authentication()
