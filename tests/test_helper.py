import pytest


def test_get_bearer_token_from_aws_gateway_authorizer_event():

    from zitadel_authorizer.helper import (
        get_bearer_token_from_aws_gateway_authorizer_event,
    )

    event = {
        "headers": {
            "authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9",
        }
    }

    token = get_bearer_token_from_aws_gateway_authorizer_event(event)
    assert token == "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9"


def test_get_bearer_token_from_aws_gateway_authorizer_event_no_auth_header():
    from zitadel_authorizer.helper import (
        get_bearer_token_from_aws_gateway_authorizer_event,
    )

    event = {
        "headers": {},
    }

    with pytest.raises(ValueError, match="No Authorization header found"):
        get_bearer_token_from_aws_gateway_authorizer_event(event)


def test_get_bearer_token_from_aws_gateway_authorizer_event_no_bearer():
    from zitadel_authorizer.helper import (
        get_bearer_token_from_aws_gateway_authorizer_event,
    )

    event = {"headers": {"authorization": "abc"}}

    with pytest.raises(ValueError, match="No Authorization header found"):
        get_bearer_token_from_aws_gateway_authorizer_event(event)
