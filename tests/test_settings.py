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
    assert str(settings.ISSUER_URL) == "https://example.com/"
    assert str(settings.INTROSPECTION_ENDPOINT) == "https://example.com/introspect"
    assert settings.APPLICATION_KEY_ARN == "test_key"
