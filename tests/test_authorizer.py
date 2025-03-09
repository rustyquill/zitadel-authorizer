import logging


def test_authorizer_from_apigateway_event(
    event_without_authorization, event_with_token, opaque_token, caplog
):
    from zitadel_authorizer.authorizer import Authorizer

    with caplog.at_level(logging.WARNING):
        authorizer = Authorizer.from_api_gateway_event(event_without_authorization)
        assert authorizer.token is None
        assert "No Authorization header found" in caplog.text

    authorizer = Authorizer.from_api_gateway_event(event_with_token)
    assert authorizer.token == opaque_token


def test_authorizer_is_jwt_token(opaque_token, jwt_token):
    from zitadel_authorizer.authorizer import Authorizer

    authorizer = Authorizer(opaque_token)
    assert authorizer.is_jwt_token() is False

    authorizer = Authorizer(jwt_token)
    assert authorizer.is_jwt_token() is True


def test_authorizer_is_opaque_token(opaque_token, jwt_token):
    from zitadel_authorizer.authorizer import Authorizer

    authorizer = Authorizer(opaque_token)
    assert authorizer.is_opaque_token() is True

    authorizer = Authorizer(jwt_token)
    assert authorizer.is_opaque_token() is False
