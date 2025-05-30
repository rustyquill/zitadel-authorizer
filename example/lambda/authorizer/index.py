from zitadel_authorizer import (
    Introspector,
    ApplicationKey,
    Authorizer,
    AuthorizerSettings,
    IntrospectorSettings,
    IntrospectionResponse,
    get_bearer_token_from_aws_gateway_authorizer_event,
)

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import event_source
from aws_lambda_powertools.utilities.data_classes.api_gateway_authorizer_event import (
    APIGatewayAuthorizerEventV2,
)

logger = Logger()


@logger.inject_lambda_context()
@event_source(data_class=APIGatewayAuthorizerEventV2)
def handler(event: APIGatewayAuthorizerEventV2, context: LambdaContext):

    logger.info("Loading introspection settings")
    introspection_settings: IntrospectorSettings = IntrospectorSettings()

    logger.info("Loading authorizer settings")
    authorizer_settings: AuthorizerSettings = AuthorizerSettings()

    logger.info(
        f"Loading application key from parameter store {introspection_settings.APPLICATION_KEY_ARN}"
    )
    application_key = ApplicationKey.from_aws_parameter_store(
        parameter_name=introspection_settings.APPLICATION_KEY_ARN
    )

    logger.info("Preparing introspector")
    introspector = Introspector(
        application_key=application_key,
        issuer_url=introspection_settings.ISSUER_URL,
        introspection_endpoint=introspection_settings.INTROSPECTION_ENDPOINT,
    )

    logger.info("Getting bearer token from event")
    bearer_token = get_bearer_token_from_aws_gateway_authorizer_event(event)
    logger.debug(f"Bearer token: {bearer_token}")

    logger.info("Introspecting token")
    introspected_token: IntrospectionResponse = introspector.introspect_token(
        token=bearer_token
    )
    logger.debug(f"Introspected token: {introspected_token}")

    # initialize the authorizer
    authorizer = Authorizer(
        required_client_id=authorizer_settings.CLIENT_ID,
        required_scopes=authorizer_settings.REQUIRED_SCOPES,
        required_roles=authorizer_settings.REQUIRED_ROLES,
    )

    response = authorizer.return_simple_authorizer_response(
        introspection_token=introspected_token
    )

    logger.info("Returning response")
    logger.debug(f"Response: {response.asdict()}")

    return response.asdict()
