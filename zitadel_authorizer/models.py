from pydantic import BaseModel
import base64
import json
from aws_lambda_powertools.utilities import parameters


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
