import pytest


def test_introspection_settings(monkeypatch):
    from zitadel_authorizer.models import IntrospectorSettings

    with pytest.raises(ValueError):
        # Test missing environment variables
        settings = IntrospectorSettings()

    monkeypatch.setenv("ISSUER_URL", "https://example.com")
    monkeypatch.setenv("INTROSPECTION_ENDPOINT", "https://example.com/introspect")
    monkeypatch.setenv("APPLICATION_KEY_ARN", "test_key")

    settings = IntrospectorSettings()
    assert settings.ISSUER_URL == "https://example.com"
    assert settings.INTROSPECTION_ENDPOINT == "https://example.com/introspect"
    assert settings.APPLICATION_KEY_ARN == "test_key"


def test_authorizer_settings(monkeypatch):
    from zitadel_authorizer.models import AuthorizerSettings

    # if no scope or roles are given we should have empty lists
    settings = AuthorizerSettings()
    assert settings.REQUIRED_SCOPES == []
    assert settings.REQUIRED_ROLES == []

    monkeypatch.setenv("REQUIRED_SCOPES", '["scope1","scope2"]')
    monkeypatch.setenv("REQUIRED_ROLES", '["role1","role2"]')

    settings = AuthorizerSettings()
    assert settings.REQUIRED_SCOPES == ["scope1", "scope2"]
    assert settings.REQUIRED_ROLES == ["role1", "role2"]
