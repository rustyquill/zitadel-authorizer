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


def test_introspection_response_inactive():
    from zitadel_authorizer.models import IntrospectionResponse

    response = IntrospectionResponse(active=False)
    assert response.active is False
    assert response.scope is None
    assert response.client_id is None
    assert response.token_type is None
    assert response.exp is None
    assert response.iat is None
    assert response.auth_time is None
    assert response.nbf is None
    assert response.sub is None
    assert response.aud is None
    assert response.amr is None
    assert response.iss is None
    assert response.jti is None
    assert response.username is None


def test_introspection_response_no_grants(introspection_response_bearer_no_grants):
    from zitadel_authorizer.models import IntrospectionResponse

    response = IntrospectionResponse(**introspection_response_bearer_no_grants)
    assert response.active is True
    assert response.scope == "openid profile email"
    assert response.client_id == "314329295906471939"
    assert response.token_type == "Bearer"
    assert response.exp == 1743901935
    assert response.iat == 1743858735
    assert response.auth_time == 1743858734
    assert response.nbf == 1743858735
    assert response.sub == "314329296560717827"
    assert response.aud == [
        "314329295268937731",
        "314329295688368131",
        "314329295906471939",
        "314329296124575747",
        "314329296342679555",
        "314329294882996227",
    ]
    assert response.amr == ["pwd"]
    assert response.iss == "http://localhost:8080"
    assert response.jti == "V2_314342508249219075-at_314342508249284611"
    assert response.username == "integration-test-user"
    assert response.name == "User User"
    assert response.given_name == "User"
    assert response.family_name == "User"
    assert response.nickname == "User"
    assert response.locale == None
    assert response.updated_at == 1743850861
    assert response.preferred_username == "integration-test-user"
    assert response.email == "integration-test-user@zitadel.localhost"
    assert response.email_verified is True
    assert response.project_roles == None


def test_introspect_response_with_grants(introspection_response_bearer_with_grants):
    from zitadel_authorizer.models import IntrospectionResponse

    response = IntrospectionResponse(**introspection_response_bearer_with_grants)
    assert response.active is True
    assert response.scope == "openid profile email"
    assert response.client_id == "314329296124575747"
    assert response.token_type == "Bearer"
    assert response.exp == 1743901935
    assert response.iat == 1743858735
    assert response.auth_time == 1743858734
    assert response.nbf == 1743858735
    assert response.sub == "314335774260592643"
    assert response.aud == [
        "314329295268937731",
        "314329295688368131",
        "314329295906471939",
        "314329296124575747",
        "314329296342679555",
        "314329294882996227",
    ]
    assert response.amr == ["pwd"]
    assert response.iss == "http://localhost:8080"
    assert response.jti == "V2_314342508350144515-at_314342508350210051"
    assert response.username == "integration-test-user-with-two-roles"
    assert response.name == "User User"
    assert response.given_name == "User"
    assert response.family_name == "User"
    assert response.nickname == "User"
    assert response.locale == None
    assert response.updated_at == 1743854722
    assert response.preferred_username == "integration-test-user-with-two-roles"
    assert response.email == "integration-test-user-with-two-roles@zitadel.localhost"
    assert response.email_verified is True
    assert response.project_roles == ["ADMIN", "USER"]
