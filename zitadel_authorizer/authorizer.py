"""
Lambda Authorizer for API Gateway to authenticate and authorize requests based on Zitadel tokens
"""

from aws_lambda_powertools.utilities.data_classes.api_gateway_authorizer_event import (
    APIGatewayAuthorizerEventV2,
    APIGatewayAuthorizerResponseV2,
)


class Authorizer:
    """
    Authorizer class to handle the authorizer logic
    """

    bearer_token: str

    def __init__(self, token: str):
        """
        Initialize the Authorizer object
        """

        self.bearer_token = token

    @classmethod
    def from_api_gateway_event(cls, event: APIGatewayAuthorizerEventV2):
        """
        Create an Authorizer object from an API Gateway Authorizer Event
        """

        parsed_event = APIGatewayAuthorizerEventV2(event)
        token = parsed_event.headers.get("authorization")

        if not token:
            raise ValueError("No Authorization header found")

        return cls(token[0].replace("Bearer ", ""))

    def is_jwt_token(self):
        """
        Check if the token is a JWT token, simply checks if token starts with ey
        """

        if not self.bearer_token.startswith("ey"):
            return False

        return True

    def is_opaque_token(self):
        """
        Check if the token is an opaque token
        """

        if self.is_jwt_token():
            return False

        return True
