import pytest
from models import ApplicationKey, IntrospectionResponse


@pytest.fixture(scope="module")
def introspector(zitadel_instance):
    from zitadel_authorizer.introspector import Introspector

    introspector = Introspector(
        application_key=ApplicationKey.from_base64_string(
            zitadel_instance.api_app_key.key_details
        ),
        issuer_url=zitadel_instance.urls.issuer_url,
        introspection_endpoint=zitadel_instance.urls.introspection_endpoint,
    )

    return introspector


def test_introspector(introspector):
    from zitadel_authorizer.introspector import Introspector

    assert introspector.issuer_url == "http://localhost:8080"
    assert (
        introspector.introspection_endpoint
        == "http://localhost:8080/oauth/v2/introspect"
    )


def test_introspector_introspect_token_invalid(introspector):
    """introspect an invalid token"""

    token: IntrospectionResponse = introspector.introspect_token("invalid_token")
    assert token.active == False


def test_introspector_introspect_token(
    introspector,
    zitadel_bearer_token_no_grants,
    zitadel_jwt_token_no_grants,
    zitadel_bearer_token_with_grants,
    zitadel_jwt_token_with_grants,
):
    """introspect different tokens"""

    token: IntrospectionResponse = None

    # no user roles should be present for a user without grants
    token = introspector.introspect_token(zitadel_bearer_token_no_grants)
    assert token.active == True
    assert token.preferred_username == "integration-test-user"
    assert token.project_roles == None

    # same should be true for jwt of the user
    token = introspector.introspect_token(zitadel_jwt_token_no_grants)
    assert token.active == True
    assert token.preferred_username == "integration-test-user"
    assert token.project_roles == None

    # do the same tests with a user which has project role grants assigned
    token = introspector.introspect_token(zitadel_bearer_token_with_grants)
    assert token.active == True
    assert token.preferred_username == "integration-test-user-with-roles"
    assert token.project_roles == ["ADMIN", "USER"]

    token = introspector.introspect_token(zitadel_jwt_token_with_grants)
    assert token.active == True
    assert token.preferred_username == "integration-test-user-with-roles"
    assert token.project_roles == ["ADMIN", "USER"]
