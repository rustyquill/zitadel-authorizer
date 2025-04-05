from aws_lambda_powertools.utilities.data_classes.api_gateway_authorizer_event import (
    APIGatewayAuthorizerEventV2,
)


def get_bearer_token_from_aws_gateway_authorizer_event(
    event: APIGatewayAuthorizerEventV2,
) -> str:
    """
    Get the bearer token from the AWS proxy event
    """

    if not isinstance(event, APIGatewayAuthorizerEventV2):
        event = APIGatewayAuthorizerEventV2(event)

    token = event.headers.get("authorization")

    if not token:
        raise ValueError("No Authorization header found")

    if "Bearer " not in token:
        raise ValueError("No Authorization header found")

    return token.replace("Bearer ", "")
