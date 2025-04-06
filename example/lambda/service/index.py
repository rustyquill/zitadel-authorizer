from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from zitadel_authorizer.middleware import (
    IsAuthenticatedMiddleware,
    ProjectRoleAuthorizationMiddleware,
)

logger = Logger()
app = APIGatewayHttpResolver(strip_prefixes=["/public", "/private"])


# this endpoint can be accessed by anyone
# of course if you're protecting the service lambda with a gateway authorizer
# the authorizer will be invoked first!
@app.get("/anyone")
def anyone():
    """
    This endpoint is open to anyone
    """

    return {
        "message": "Anyone can access this endpoint",
    }


# this endpoint is only accessible for authenticated users
# e.g. the isauthenticated middleware checks if the authorizer context is present
@app.get("/authenticated", middlewares=[IsAuthenticatedMiddleware()])
def authenticated():
    """
    This endpoint is only accessible for authenticated users
    """

    return {
        "message": "Authenticated users can access this endpoint",
    }


# this endpoint is only accessible for users with the project role "demo"
# you can create a project role in zitadel and assign it to a user!
@app.get("/demo", middlewares=[ProjectRoleAuthorizationMiddleware(roles=["demo"])])
def demo():
    """
    This endpoint is only accessible for users with the project role "demo"
    """

    return {
        "message": "Users with the project role 'demo' can access this endpoint",
    }


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
