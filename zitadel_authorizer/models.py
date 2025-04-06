from pydantic import BaseModel, Field
import base64
import json
from aws_lambda_powertools.utilities import parameters
from typing import List, Optional, Dict
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from pydantic_settings import BaseSettings


class IntrospectorSettings(BaseSettings):
    """
    Settings for the Introspector.
    """

    ISSUER_URL: str
    INTROSPECTION_ENDPOINT: str
    APPLICATION_KEY_ARN: str


class AuthorizerSettings(BaseSettings):
    """
    Settings for the Authorizer.
    """

    CLIENT_ID: Optional[str] = None
    REQUIRED_SCOPES: List[str] = []
    REQUIRED_ROLES: List[str] = []


class ApplicationKey(BaseModel):
    """
    ApplicationKey class to handle the application key
    """

    type: str
    keyId: str
    key: str
    appId: str
    clientId: str

    @staticmethod
    def from_base64_string(base64_string: str):
        """
        Create an ApplicationKey object from a base64 string
        """

        key_data = base64.b64decode(base64_string).decode("utf-8")
        key_json = json.loads(key_data)
        return ApplicationKey(**key_json)

    @staticmethod
    def from_aws_parameter_store(parameter_name: str, secure_string: bool = True):
        """
        Create an ApplicationKey object from an AWS Parameter Store parameter
        We only support a base64 encoded string inside the parameter store!
        """

        key_data = parameters.get_parameter(parameter_name, decrypt=secure_string)
        return ApplicationKey.from_base64_string(key_data)


# zitadel passes the project roles in the format:
# "urn:zitadel:iam:org:project:roles": {
# {
#     'ROLEA': {'PROJECT_ID': 'ZITADEL_DOMAIN'},
#     'ROLEB': {'PROJECT_ID': 'ZITADEL_DOMAIN'}
# }
# we are only interested in the role keys!
def convert_project_roles_to_list(v: Dict[str, Dict[str, str]]) -> List[str]:
    return v.keys()


PROJECT_ROLES = Annotated[List[str], BeforeValidator(convert_project_roles_to_list)]


class IntrospectionResponse(BaseModel):
    """
    Introspection response class to handle the response from the introspection endpoint
    """

    # active is the only required field,
    # if a token is not active the other fields are not passed
    active: bool

    scope: Optional[str] = None
    client_id: Optional[str] = None
    token_type: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    auth_time: Optional[int] = None
    nbf: Optional[int] = None
    sub: Optional[str] = None
    aud: Optional[List[str]] = None
    amr: Optional[List[str]] = None
    iss: Optional[str] = None
    jti: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    nickname: Optional[str] = None
    locale: Optional[str] = None
    updated_at: Optional[int] = None
    preferred_username: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None

    project_roles: Optional[PROJECT_ROLES] = Field(
        alias="urn:zitadel:iam:org:project:roles", default=None
    )

    def has_scopes(self, scopes: List[str]) -> bool:
        """
        Check if the token has the required scopes
        """

        if not self.scope:
            return False

        token_scopes = self.scope.split(" ")
        return all(scope in token_scopes for scope in scopes)

    def has_roles(self, roles: List[str]) -> bool:
        """
        Check if the token has the required roles
        """

        if not self.project_roles:
            return False

        return all(role in self.project_roles for role in roles)
