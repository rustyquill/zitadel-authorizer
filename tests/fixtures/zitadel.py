import pytest
from testcontainers.compose import DockerCompose
from typing import Dict
import json
import concurrent.futures
from .zitadel_integration import (
    ZitadelIntegration,
    ZitadelProject,
    ZitadelWebapp,
    ZitadelApiApp,
    ZitadelApiAppKey,
    ZitadelUser,
    ZitadelUrls,
    ZitadelToken,
)


@pytest.fixture(scope="session", autouse=False)
def zitadel_compose(request):
    compose = DockerCompose(context=".", compose_file_name="docker-compose.yaml")
    compose.start()

    def teardown():
        compose.stop()

    request.addfinalizer(teardown)

    # wait for the container to be up
    zitadel = ZitadelIntegration()
    zitadel.load_pat()
    zitadel.test_connectivty()

    yield zitadel


@pytest.fixture(scope="session", autouse=False)
def zitadel_instance(zitadel_compose):
    # prepare test project with roles
    project = ZitadelProject(**zitadel_compose.create_project(name="integration-test"))
    zitadel_compose.create_project_roles(project_id=project.id, roles=["ADMIN", "USER"])

    # the additional project is only used to assign roles to test the introspection model
    # to ensure the POWERUSER role is not passed in the introspection response!
    additional_project = ZitadelProject(
        **zitadel_compose.create_project(name="integration-test-additional-project")
    )
    zitadel_compose.create_project_roles(
        project_id=additional_project.id, roles=["POWERUSER"]
    )

    # the api app is used by the introspector to introspect the opaque user token
    api_app = ZitadelApiApp(
        **zitadel_compose.create_api_app(
            project_id=project.id, name="integration-test-api"
        )
    )
    api_app_key = ZitadelApiAppKey(
        **zitadel_compose.create_api_app_key(project_id=project.id, app_id=api_app.id)
    )

    # initialize webapps with bearer (opaque) and jwt tokens
    # with or without token assertions
    web_apps = dict(
        bearer=ZitadelWebapp(
            **zitadel_compose.create_web_app(
                project_id=project.id,
                name="integration-test-web-bearer",
                access_token_type="OIDC_TOKEN_TYPE_BEARER",
            )
        ),
        jwt=ZitadelWebapp(
            **zitadel_compose.create_web_app(
                project_id=project.id,
                name="integration-test-web-jwt",
                access_token_type="OIDC_TOKEN_TYPE_JWT",
            )
        ),
    )

    # initialize three users, one without roles, one with a single role
    # and one with two roles
    users = dict(
        user_no_grants=ZitadelUser(
            **{
                **zitadel_compose.create_user(
                    username="integration-test-user",
                    password="integration-test-password",
                ),
                **{"password": "integration-test-password"},
            }
        ),
        user_with_grants=ZitadelUser(
            **{
                **zitadel_compose.create_user(
                    username="integration-test-user-with-roles",
                    password="integration-test-password",
                ),
                **{"password": "integration-test-password"},
            }
        ),
    )
    zitadel_compose.add_user_grant(
        project_id=project.id,
        user_id=users.get("user_with_grants").id,
        role_keys=["ADMIN", "USER"],
    )
    zitadel_compose.add_user_grant(
        project_id=additional_project.id,
        user_id=users.get("user_with_grants").id,
        role_keys=["POWERUSER"],
    )

    class ZitadelInstance:
        def __init__(self):
            self.urls: ZitadelUrls = ZitadelUrls()
            self.project: ZitadelProject = project
            self.api_app: ZitadelApiApp = api_app
            self.api_app_key: ZitadelApiAppKey = api_app_key
            self.web_apps: Dict[str, ZitadelWebapp] = web_apps
            self.users: Dict[str, ZitadelUser] = users

    yield ZitadelInstance()


@pytest.fixture(scope="session", autouse=False)
def zitadel_tokens(zitadel_compose, zitadel_instance):
    """lease all tokens for all users and web apps, parallelized for performance"""

    def lease_token(user_key, user_value, web_app_key, web_app_value):
        return dict(
            user=user_key,
            web_app=web_app_key,
            token=ZitadelToken(
                **zitadel_compose.login_user(
                    username=user_value.username,
                    password=user_value.password,
                    client_id=web_app_value.client_id,
                )
            ),
        )

    tokens = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for user_key, user_value in zitadel_instance.users.items():
            for web_app_key, web_app_value in zitadel_instance.web_apps.items():
                futures.append(
                    executor.submit(
                        lease_token,
                        user_key,
                        user_value,
                        web_app_key,
                        web_app_value,
                    )
                )

        for future in concurrent.futures.as_completed(futures):
            tokens.append(future.result())

    yield tokens


def _return_token(tokens, user, app):
    """helper function to return the token for a specific user and web app"""
    for token in tokens:
        if token["user"] == user and token["web_app"] == app:
            return token["token"].access_token


@pytest.fixture
def zitadel_bearer_token_no_grants(zitadel_tokens):

    return _return_token(zitadel_tokens, "user_no_grants", "bearer")


@pytest.fixture
def zitadel_jwt_token_no_grants(zitadel_tokens):
    return _return_token(zitadel_tokens, "user_no_grants", "jwt")


@pytest.fixture
def zitadel_bearer_token_with_grants(zitadel_tokens):

    return _return_token(zitadel_tokens, "user_with_grants", "bearer")


@pytest.fixture
def zitadel_jwt_token_with_grants(zitadel_tokens):
    return _return_token(zitadel_tokens, "user_with_grants", "jwt")


@pytest.fixture
def opaque_token():
    """placeholder token"""
    return "HEFx_abcdefghijklmnopqrstuvwxyz123456789-abcdefghijklmno_AB_pqrstuvwxyz123456789abcdefghijklmnopqrstuvwx"


@pytest.fixture
def jwt_token():
    """placeholder jwt"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"


@pytest.fixture
def api_app_key():
    """api key generated on local dev instance"""

    return "eyJ0eXBlIjoiYXBwbGljYXRpb24iLCJrZXlJZCI6IjMxMDQxMDEzNzgyOTM3NjAwMyIsImtleSI6Ii0tLS0tQkVHSU4gUlNBIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUVvd0lCQUFLQ0FRRUEwRWhKTTFhWHBqenY5ZXFaS2dNU0x5TUNxdnJWbmFESGZLbGFrUzhwSjVHQU9wWjhcbjVURVMrL0JxNi9nRVNmMGlvK1ZFRmNVbXhiNm1UOWk2Uk5zY3FLRGo3MHRvV0plU1pER2Y0TGF5dmhtSlZMY1Vcbnd4N0xzYzFucUpJYVhGNG9XazNTWW03dVRqZlhlY3NORTJNT2RhMXg1QmErMTVLZ1ZMNGMxWjJiM1l3TS9Oalpcbnh2VTJRWGtkY1FBTHFQc09BdUNuU2lhdUh6c3hDQmNrMFRuYkkydTJBQXpvVm5jVXJxcDNKMmhvcDhnUk1oOGFcbldnTXAzVVBnMW4wdHpzNm9UbzJWOVczWlkzYzhPTFQ2enBLTWU0L2pEeWRMVVp0SzhjbnQ2NUhSaktDQzM1ZklcbmEraUJmYXczTUYyc1k5ZHdEaXBJbXV1cUJqM3JFNDF1VlV0VEp3SURBUUFCQW9JQkFERWdlN09TUHg3RXpNeXlcblV3SW55MGcyOTlBZ2JmWktFQU9GWm9sTUdHYnUyTkg0NE9pbVZKWDhOUndIV2V1aHUyUHhGY2dVd25wdDU0aDVcbjFDV2RrUHJ0U0JZUE1VT0VMTkZaS3g2enVTRkJvTFRNb2ljTHdudmp1UWwzdktRQXlYL1RUMFpNYUFVbkFyb0ZcbmZNWVAzVDlBYzlhYXp0VEdEdTh1RUZzS1c5TTdZbmFnYStDQVFyTGxHWWppK2VXbDBLWXJhOFJHN2xrdzYwRDdcbjhsVEp1dENzb1JLUllkNTkvbDhVVUVOQUN2b05rWEViZjV5ZVVERTZvRkpmSjJZdENianNFSWl4d1FUeUFUcTFcbkV5RUQwcC9KOWxBYmFUWnk1Z0xnQ3BDckdZS2d2dHIxQ2FLaHhCNEJIQldVNHV2ZTB4aUpnMGpxTHVmSmgrOW5cbnV0NDRNUkVDZ1lFQTRYRzk5SldjTzd6RnRJdU5KUjVsTTZUb0dvS2pZMHI1OHkyUWd0QzRpRTB6L0lTLzljTVdcbkI4NUdXdW96dWlqK1dqc1F6N1JRWSttdHl5N3ZBd2lLekJpb0lOanYvSDNTQkZsTjNaOFdDaDF6QVZaSVlwTGFcbnVJRzlnUm1FOVRyOFlhcVhacU5LQ0NwcXhxUGlTM0lRQUl5Z2JHSlhSYWV3UTE0b25DYWRscXNDZ1lFQTdJTVRcbksyVnB3R2M1dnRrZWRhYTE4WHlLbGY0RkowRUtKd0JEM3NUSkFaVHhncFFpY2QyYm1JQks4cytJcEdRM0R3NzBcblQrRHI5aWJQL1VLYnIwWUs1RnYxQUMyVDdVZm13NGxRUzYvemJGa1JqV1J5Z3hpVHlKQVRueS8wNlJOTklITTlcblVSQUJ3dVNibUtYblVLTEppaFNYRkRDc0hFTmkxVHhmSHBoOFpYVUNnWUVBM2RVVkRDRlhEVFR2K1hyRDFQMTJcbnFYMmY0YzRnUmFqV0VDSUtxNTREcGlNSmYzV0VpYWgvK2doUUZFK1Z2SjF2d291U1BENzZSNFg5dkF1ZnBnVjJcbnhlT1JORmtpcy9sK2VVY0Nwb3RPblg5aTFiTDRJUDdOOTNXNmFka1ppbENUWE9zR2RUbEJ0STFBYWR1QzVhZ0RcbjlQWnJPSnIvc3d1UkZva0ZQcm1Fb1djQ2dZQWFMcHgxcG1GaG1rdkxNOC9xYUUwbDhZcUo5amZ0MDRaak1PVlNcbmlPaFRrNEIwMng5QkNhNUs0SkRyZGt3REh0RDFpc3RDK0h4R29KOVB3d3JuQ1ZMMVdyU3hrMW9YMzJqTlpxc0xcbjVldUZxQXFJWTRGRnYvZkVNU2JxN1cwb1RDbXltTzlGeFFiYzQxL1NNek43T3JvaTNncW5nb2ZiRFI2b3lta2hcblF2SXFiUUtCZ0hLalBpQTkrcmZKbUpEUzQwQ0pKbVNmalpQQXhld0ZNUVpoZlluTFpmV1h3SU9MK0lKZjZtUGRcbnViam4vc0RwL3pobWtOTnh4ZzlFWTNzL0orYVpleXlXZlU1WGJuTW9GYWZoV3ROL3NTZnMyRldkelFOODM0U3RcbjltaUVmcFZYUkh1cDYvdkU1T2VGNlJ5NzdENTBYazRHOU5wQ040N3VyQy9jSExDdFVqdVBcbi0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tXG4iLCJhcHBJZCI6IjMxMDQwOTg0OTQ5NjE0MTgyNyIsImNsaWVudElkIjoiMzEwNDA5ODQ5NDk2MjA3MzYzIn0="


@pytest.fixture
def introspection_response_bearer_no_grants():
    return json.loads(
        """{
            "active": true,
            "scope": "openid profile email",
            "client_id": "314329295906471939",
            "token_type": "Bearer",
            "exp": 1743901935,
            "iat": 1743858735,
            "auth_time": 1743858734,
            "nbf": 1743858735,
            "sub": "314329296560717827",
            "aud": [
                "314329295268937731",
                "314329295688368131",
                "314329295906471939",
                "314329296124575747",
                "314329296342679555",
                "314329294882996227"
            ],
            "amr": ["pwd"],
            "iss": "http://localhost:8080",
            "jti": "V2_314342508249219075-at_314342508249284611",
            "username": "integration-test-user",
            "name": "User User",
            "given_name": "User",
            "family_name": "User",
            "nickname": "User",
            "locale": null,
            "updated_at": 1743850861,
            "preferred_username": "integration-test-user",
            "email": "integration-test-user@zitadel.localhost",
            "email_verified": true
        }"""
    )


@pytest.fixture
def introspection_response_bearer_with_grants():
    return json.loads(
        """{
            "active": true,
            "amr": ["pwd"],
            "aud": [
                "314329295268937731",
                "314329295688368131",
                "314329295906471939",
                "314329296124575747",
                "314329296342679555",
                "314329294882996227"
            ],
            "auth_time": 1743858734,
            "client_id": "314329296124575747",
            "email": "integration-test-user-with-two-roles@zitadel.localhost",
            "email_verified": true,
            "exp": 1743901935,
            "family_name": "User",
            "given_name": "User",
            "iat": 1743858735,
            "iss": "http://localhost:8080",
            "jti": "V2_314342508350144515-at_314342508350210051",
            "locale": null,
            "name": "User User",
            "nbf": 1743858735,
            "nickname": "User",
            "preferred_username": "integration-test-user-with-two-roles",
            "scope": "openid profile email",
            "sub": "314335774260592643",
            "token_type": "Bearer",
            "updated_at": 1743854722,
            "urn:zitadel:iam:org:project:314329294882996227:roles": {
                "ADMIN": {"314329284565073923": "zitadel.localhost"},
                "USER": {"314329284565073923": "zitadel.localhost"}
            },
            "urn:zitadel:iam:org:project:roles": {
                "ADMIN": {"314329284565073923": "zitadel.localhost"},
                "USER": {"314329284565073923": "zitadel.localhost"}
            },
            "username": "integration-test-user-with-two-roles"
        }"""
    )
