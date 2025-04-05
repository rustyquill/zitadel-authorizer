import pytest
from testcontainers.compose import DockerCompose
from pydantic import BaseModel, Field
from typing import Dict, List
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


@pytest.fixture(scope="session", autouse=True)
def zitadel_compose(request):
    compose = DockerCompose(context=".", compose_file_name="docker-compose.yaml")
    compose.start()

    def teardown():
        # TODO: enable stop after setup
        # compose.stop()
        pass

    request.addfinalizer(teardown)

    zitadel = ZitadelIntegration()
    zitadel.load_pat()
    zitadel.test_connectivty()

    # Possible values: [OIDC_TOKEN_TYPE_BEARER, ]

    # prepare test project with roles
    project = ZitadelProject(**zitadel.create_project(name="integration-test"))
    zitadel.create_project_roles(project_id=project.id, roles=["ADMIN", "USER"])

    # the api app is used by the introspector to introspect the opaque user token
    api_app = ZitadelApiApp(
        **zitadel.create_api_app(project_id=project.id, name="integration-test-api")
    )
    api_app_key = ZitadelApiAppKey(
        **zitadel.create_api_app_key(project_id=project.id, app_id=api_app.id)
    )

    # create webapps with bearer (opaque) and jwt tokens
    web_apps = dict(
        bearer=ZitadelWebapp(
            **zitadel.create_web_app(
                project_id=project.id,
                name="integration-test-web-bearer",
                access_token_type="OIDC_TOKEN_TYPE_BEARER",
            )
        ),
        bearer_with_assertions=ZitadelWebapp(
            **zitadel.create_web_app(
                project_id=project.id,
                name="integration-test-web-bearer-with-assertions",
                access_token_type="OIDC_TOKEN_TYPE_BEARER",
                access_token_role_assertion=True,
                id_token_role_assertion=True,
                id_token_userinfo_assertion=True,
            )
        ),
        jwt=ZitadelWebapp(
            **zitadel.create_web_app(
                project_id=project.id,
                name="integration-test-web-jwt",
                access_token_type="OIDC_TOKEN_TYPE_JWT",
            )
        ),
        jwt_with_assertions=ZitadelWebapp(
            **zitadel.create_web_app(
                project_id=project.id,
                name="integration-test-web-jwt-with-assertions",
                access_token_type="OIDC_TOKEN_TYPE_JWT",
                access_token_role_assertion=True,
                id_token_role_assertion=True,
                id_token_userinfo_assertion=True,
            )
        ),
    )

    # create one user without any authorizations and one user with authorizations for the
    # test project
    # TODO: assign authorizations
    user = ZitadelUser(
        **{
            **zitadel.create_user(
                username="integration-test-user",
                password="integration-test-password",
            ),
            **{"password": "integration-test-password"},
        }
    )

    # TODO: store tokens
    # user.token = ZitadelToken(
    #     **zitadel.login_user(
    #         username=user.username,
    #         password=user.password,
    #         client_id=web_app.client_id,
    #     )
    # )

    class ZitadelCompose:
        def __init__(self):
            self.zitadel = zitadel
            self.urls: ZitadelUrls = ZitadelUrls()
            self.project: ZitadelProject = project
            self.api_app: ZitadelApiApp = api_app
            self.api_app_key: ZitadelApiAppKey = api_app_key
            self.web_apps: Dict[str, ZitadelWebapp] = web_apps
            self.user: ZitadelUser = user

    yield ZitadelCompose()


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
