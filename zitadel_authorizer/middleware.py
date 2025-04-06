"""
API Gateway Middleware to authorize requests based of Zitadel Scopes
The lambda authorizer passes the introspected token values as context to
the services.

You can use mapping templates to modify the request send to the integration,
but using lambda proxy the authorizer context is accessible in the received
event in `request_context.authorizer.get_lambda` using the proxy event data source
https://github.com/aws-powertools/powertools-lambda-python/blob/develop/aws_lambda_powertools/utilities/data_classes/api_gateway_proxy_event.py
"""

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.middlewares import (
    BaseMiddlewareHandler,
    NextMiddleware,
)
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from typing import List
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2

logger = Logger()


class IsAuthenticatedMiddleware(BaseMiddlewareHandler):
    """
    Middleware to check if the user is authenticated
    """

    def handler(
        self, app: APIGatewayHttpResolver, next_middleware: NextMiddleware
    ) -> Response:
        """
        Handle the request and check if the user is authenticated
        """

        logger.debug("Checking if user is authenticated")

        # Check if the user is authenticated
        if not app.current_event.request_context.authorizer.get_context():
            logger.debug("User is not authenticated")
            return Response(
                status_code=401,
                body="Unauthorized",
            )

        return next_middleware(app)


class ProjectRoleAuthorizationMiddleware(BaseMiddlewareHandler):
    """
    Middleware to authorize requests based on the project role(s) of the user
    """

    def __init__(self, roles: List[str]):
        """
        Initialize the middleware with the required roles
        """

        super().__init__()
        self.roles = roles

    def get_roles_from_context(self, event: APIGatewayProxyEventV2) -> List[str]:
        """
        Get the roles from the current event
        """

        authorizer_context = event.request_context.authorizer.get_context()

        return authorizer_context.get("project_roles", [])

    def handler(
        self, app: APIGatewayHttpResolver, next_middleware: NextMiddleware
    ) -> Response:
        """
        Handle the request and check if the user has the required roles
        """

        logger.debug("Checking if user has the required roles")

        context_roles = self.get_roles_from_context(app.current_event)

        # Check if the user has the required roles
        if not any(role in self.roles for role in context_roles):
            logger.debug("User does not have the required roles")
            return Response(
                status_code=403,
                body="Forbidden",
            )

        return next_middleware(app)
