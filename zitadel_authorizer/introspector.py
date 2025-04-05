"""
The introspector is used to introspect opaque tokens received from the API Gateway.
original from: https://github.com/zitadel/examples-api-access-and-token-introspection/blob/main/api-jwt/validator.py
"""

from authlib.oauth2.rfc7662 import IntrospectTokenValidator
import requests
import time
import jwt

from .models import ApplicationKey, IntrospectionResponse


class Introspector(IntrospectTokenValidator):
    """
    Introspector class to handle the introspection logic
    """

    def __init__(
        self,
        application_key: ApplicationKey,
        issuer_url: str,
        introspection_endpoint: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.application_key = application_key
        self.issuer_url = issuer_url
        self.introspection_endpoint = introspection_endpoint

    def introspect_token(
        self,
        token: str,
    ):
        """
        introspect the token using the introspection endpoint
        """

        payload = dict(
            iss=self.application_key.clientId,
            sub=self.application_key.clientId,
            aud=self.issuer_url,
            exp=int(time.time()) + 60 * 60,  # Expires in 1 hour
            iat=int(time.time()),
        )

        headers = dict(
            alg="RS256",
            kid=self.application_key.keyId,
        )

        jwt_token = jwt.encode(
            payload,
            self.application_key.key,
            algorithm="RS256",
            headers=headers,
        )

        data = dict(
            client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            client_assertion=jwt_token,
            token=token,
        )

        response = requests.post(
            url=self.introspection_endpoint,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        )
        response.raise_for_status()

        return IntrospectionResponse(**response.json())
