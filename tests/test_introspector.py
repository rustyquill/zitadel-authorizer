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


def test_introspector_introspect_token(introspector, zitadel_tokens):
    """introspect different tokens"""

    import json

    for t in zitadel_tokens:
        access_token = t["token"].access_token

        token = introspector.introspect_token(access_token)
        print(json.dumps(token, indent=4))
