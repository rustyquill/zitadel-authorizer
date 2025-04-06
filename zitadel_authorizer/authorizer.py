"""
Lambda Authorizer for API Gateway to authenticate and authorize requests based on Zitadel tokens
"""

from typing import List
from .models import IntrospectionResponse


class Authorizer:
    """
    Authorizer class to handle the authorizer logic
    """

    def __init__(
        self,
        required_scopes: List[str] = [],
        required_roles: List[str] = [],
    ):
        """
        Initialize the Authorizer object
        """

        self.required_scopes = required_scopes
        self.required_roles = required_roles

    def is_authorized(self, introspection_token: IntrospectionResponse):
        """
        Check if the token is authorized based on the required scopes and roles
        """

        if not introspection_token.active:
            return False

        if self.required_scopes and not introspection_token.has_scopes(
            self.required_scopes
        ):
            return False

        if self.required_roles and not introspection_token.has_roles(
            self.required_roles
        ):
            return False

        return True

    def return_simple_authorizer_response(
        self, introspection_token: IntrospectionResponse
    ) -> APIGatewayAuthorizerResponseV2:
        """
        Return a simple authorizer response
        """

        return APIGatewayAuthorizerResponseV2(
            authorize=self.is_authorized(introspection_token=introspection_token),
            context=introspection_token.model_dump(),
        )
