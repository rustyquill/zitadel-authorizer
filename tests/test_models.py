import pytest
from moto import mock_aws


def test_application_key_from_base64_string(api_app_key):
    from zitadel_authorizer.models import ApplicationKey

    key = ApplicationKey.from_base64_string(api_app_key)
    assert key.type == "application"
    assert key.keyId == "310410137829376003"
    assert key.key.startswith(
        "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0EhJM1aXpjzv9eqZKgMSLyMCqvrVnaDHfKlakS8pJ5GAOpZ8"
    )
    assert key.appId == "310409849496141827"
    assert key.clientId == "310409849496207363"


@mock_aws
def test_application_key_from_aws_parameter_store(ssm, api_app_key):
    from zitadel_authorizer.models import ApplicationKey

    ssm.put_parameter(
        Name="test",
        Value=api_app_key,
        Type="SecureString",
    )

    key = ApplicationKey.from_aws_parameter_store("test")
    assert key.type == "application"
    assert key.keyId == "310410137829376003"
    assert key.key.startswith(
        "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0EhJM1aXpjzv9eqZKgMSLyMCqvrVnaDHfKlakS8pJ5GAOpZ8"
    )
    assert key.appId == "310409849496141827"
    assert key.clientId == "310409849496207363"
