import pytest

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2

from zitadel_authorizer.middleware import Response


def test_get_roles_from_context(
    aws_api_gateway_proxy_event_no_authorizer,
    aws_api_gateway_proxy_event_with_authorizer,
):
    from zitadel_authorizer.middleware import ProjectRoleAuthorizationMiddleware

    event_no_roles = APIGatewayProxyEventV2(aws_api_gateway_proxy_event_no_authorizer)
    event_with_roles = APIGatewayProxyEventV2(
        aws_api_gateway_proxy_event_with_authorizer
    )

    middleware = ProjectRoleAuthorizationMiddleware(roles=[])

    assert middleware.get_roles_from_context(event_no_roles) == []
    assert middleware.get_roles_from_context(event_with_roles) == ["example"]


def test_middleware_handler(
    aws_api_gateway_proxy_event_no_authorizer,
    aws_api_gateway_proxy_event_with_authorizer,
):

    from zitadel_authorizer.middleware import ProjectRoleAuthorizationMiddleware

    class MockApp:
        def __init__(self, event):
            self.current_event = event

    class MockNextMiddleware:
        def __call__(self, app):
            return True

    middleware = ProjectRoleAuthorizationMiddleware(roles=["example"])
    event_no_roles = APIGatewayProxyEventV2(aws_api_gateway_proxy_event_no_authorizer)
    event_with_roles = APIGatewayProxyEventV2(
        aws_api_gateway_proxy_event_with_authorizer
    )

    # test without roles
    result = middleware.handler(
        MockApp(event_no_roles),
        MockNextMiddleware(),
    )

    assert result, isinstance(Response)
    assert result.status_code == 403
    assert result.body == "Forbidden"

    # test with matching roles
    assert (
        middleware.handler(
            MockApp(event_with_roles),
            MockNextMiddleware(),
        )
        is True
    )

    # test with non-matching roles
    middleware = ProjectRoleAuthorizationMiddleware(roles=["other_role"])
    result = middleware.handler(
        MockApp(event_with_roles),
        MockNextMiddleware(),
    )
    assert result, isinstance(Response)
    assert result.status_code == 403
    assert result.body == "Forbidden"
