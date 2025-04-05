"""
The introspector is used to introspect opaque tokens received from the API Gateway.
original from: https://github.com/zitadel/examples-api-access-and-token-introspection/blob/main/api-jwt/validator.py
"""

from authlib.oauth2.rfc7662 import IntrospectTokenValidator
import requests
import time
import jwt

from models import ApplicationKey


class Introspector(IntrospectTokenValidator):
    """
    Introspector class to handle the introspection logic
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def introspect_token(
        self,
        application_key: ApplicationKey,
        token: str,
        zitadel_domain: str,
        zitadel_introspection_endpoint: str,
    ):
        """
        introspect the token using the introspection endpoint
        """

        payload = dict(
            iss=application_key.clientId,
            sub=application_key.clientId,
            aud=zitadel_domain,
            exp=int(time().time()) + 60 * 5,
            iat=int(time().time()),
        )

        headers = dict(
            alg="RS256",
            kid=application_key.keyId,
        )

        jwt_token = jwt.encode(
            payload,
            application_key.key,
            algorithm="RS256",
            headers=headers,
        )

        data = dict(
            client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            client_assertion=jwt_token,
            token=token,
        )

        response = requests.post(
            url=zitadel_introspection_endpoint,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        )
        print(response.json())
