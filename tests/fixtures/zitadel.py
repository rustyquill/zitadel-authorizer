import pytest
import requests
import time
import pkce


class ZitadelIntegration:
    base_url: str = "http://localhost:8080"
    pat: str
    session: requests.Session

    def __init__(self):
        pass

    def load_pat(self, pat_file: str = "tests/docker/zitadel-admin-sa.pat") -> str:
        with open(pat_file, "r") as f:
            self.pat = f.read().strip()

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.pat}",
            }
        )

    def me(self):
        r = self.session.get(f"{self.base_url}/management/v1/orgs/me")
        r.raise_for_status()
        return r.json()

    def test_connectivty(self):
        for _ in range(5):
            try:
                self.me()
                return
            except Exception as e:
                pass
            time.sleep(1)

        raise Exception("Could not connect to Zitadel")

    def get_project(self, name: str):
        r = self.session.post(f"{self.base_url}/management/v1/projects/_search")
        for result in r.json()["result"]:
            if result["name"] == name:
                return result

        return None

    def get_app(self, project_id: str, name: str):
        r = self.session.post(
            f"{self.base_url}/management/v1/projects/{project_id}/apps/_search"
        )
        for result in r.json()["result"]:
            if result["name"] == name:
                return result

        return None

    def create_project(
        self,
        name: str,
        project_role_assertion: bool = False,
        project_role_check: bool = False,
        has_project_check: bool = False,
        private_label_setting: str = "PRIVATE_LABELING_SETTING_UNSPECIFIED",
    ):
        r = self.session.post(
            f"{self.base_url}/management/v1/projects",
            json={
                "name": name,
                "projectRoleAssertion": project_role_assertion,
                "projectRoleCheck": project_role_check,
                "hasProjectCheck": has_project_check,
                "privateLabelingSetting": private_label_setting,
            },
        )
        # ignore 200 and 409
        if r.status_code not in [200, 409]:
            r.raise_for_status()

        return r.json()

    def create_api_app(self, project_id: str, name: str):
        r = self.session.post(
            f"{self.base_url}/management/v1/projects/{project_id}/apps/api",
            json={
                "name": name,
                "authMethodType": "API_AUTH_METHOD_TYPE_PRIVATE_KEY_JWT",
            },
        )
        # ignore 200 and 409
        if r.status_code not in [200, 409]:
            r.raise_for_status()
        return r.json()

    def create_api_app_key(self, project_id: str, app_id: str):
        r = self.session.post(
            f"{self.base_url}/management/v1/projects/{project_id}/apps/{app_id}/keys",
            json={
                "type": "KEY_TYPE_JSON",
                "expirationDate": "2519-04-01T08:45:00.000000Z",
            },
        )

        r.raise_for_status()
        return r.json()

    def create_web_app(self, project_id: str, name: str):
        r = self.session.post(
            f"{self.base_url}/management/v1/projects/{project_id}/apps/oidc",
            json={
                "name": name,
                "responseTypes": ["OIDC_RESPONSE_TYPE_CODE"],
                "grantTypes": ["OIDC_GRANT_TYPE_AUTHORIZATION_CODE"],
                "redirectUris": ["http://localhost:1234"],
                "appType": "OIDC_APP_TYPE_WEB",
                "authMethodType": "OIDC_AUTH_METHOD_TYPE_NONE",
                "devMode": True,
            },
        )
        # ignore 200 and 409
        if r.status_code not in [200, 409]:
            r.raise_for_status()
        return r.json()

    def create_user(self, username: str, password: str):

        r = self.session.post(
            f"{self.base_url}/v2/users/human",
            json={
                "username": username,
                "profile": {
                    "givenName": "User",
                    "familyName": "User",
                    "nickName": "User",
                },
                "email": {
                    "email": f"{username}@zitadel.localhost",
                    "isVerified": True,
                },
                "password": {
                    "password": password,
                    "changeRequired": False,
                },
            },
        )
        # ignore 200 and 409
        if r.status_code not in [200, 409]:
            r.raise_for_status()
        return r.json()

    def login_user(self, username: str, password: str, client_id: str):
        # first call the authorize endpoint, this redirects to the login page
        # dont follow the redirect to collect the request id and the zitadel user agent cookie
        login_session = requests.Session()
        # # fake user agent
        # login_session.headers.update(
        #     {
        #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        #     }
        # )
        code_verifier, code_challenge = pkce.generate_pkce_pair()

        r = requests.get(
            url=f"{self.base_url}/oauth/v2/authorize",
            allow_redirects=False,
            params={
                "client_id": client_id,
                "response_type": "code",
                "scope": "openid profile email",
                "redirect_uri": "http://localhost:1234",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            },
        )
        r.raise_for_status()

        # the location heasder contains the request id
        # lets extract id before following the link
        request_id = r.headers["Location"].split("authRequestID=")[1]
        zitadel_user_agent = r.cookies.get_dict().get("zitadel.useragent")

        # navigate to the login page to get the crsf token and crsf cookie
        r = requests.get(
            f"{self.base_url}{r.headers['Location']}",
            allow_redirects=False,
            cookies={"zitadel.useragent": zitadel_user_agent},
        )
        r.raise_for_status()

        # get the zitadel csrf cookie
        zitadel_login_csrf = r.cookies.get_dict().get("zitadel.login.csrf")
        gorilla_csrf_token = None
        # parse the login page for the gorilla crsf token
        # <input type="hidden" name="gorilla.csrf.Token" value="d7vfg2exNvgkdP/pDCHXX4RXAaKIyn0SLChublQfU6SQC2TZ5vMD5R2S6SHPlD2o1gfIGlqo8xLKjdnUjELrJA==">
        for line in r.text.split("\n"):
            if "gorilla.csrf.Token" in line:
                gorilla_csrf_token = line.split('value="')[1].split('"')[0]

        # call the loginname endpoint with the request id and the user credentials
        r = requests.post(
            url=f"{self.base_url}/ui/login/loginname",
            allow_redirects=False,
            data={
                "gorilla.csrf.Token": gorilla_csrf_token,
                "authRequestID": request_id,
                "loginName": username,
            },
            cookies={
                "zitadel.useragent": zitadel_user_agent,
                "zitadel.login.csrf": zitadel_login_csrf,
            },
        )
        for line in r.text.split("\n"):
            if "gorilla.csrf.Token" in line:
                gorilla_csrf_token = line.split('value="')[1].split('"')[0]

        # lets call the password endpoint with the request id and the user credentials
        r = requests.post(
            url=f"{self.base_url}/ui/login/password",
            allow_redirects=False,
            data={
                "gorilla.csrf.Token": gorilla_csrf_token,
                "authRequestID": request_id,
                "loginName": username,
                "password": password,
            },
            cookies={
                "zitadel.useragent": zitadel_user_agent,
                "zitadel.login.csrf": zitadel_login_csrf,
            },
        )
        r.raise_for_status()

        # finally call the authorize endpoint with the request id to receive the token code
        r = requests.get(
            url=r.headers["Location"],
            allow_redirects=False,
            cookies={
                "zitadel.useragent": zitadel_user_agent,
                "zitadel.login.csrf": zitadel_login_csrf,
            },
        )
        r.raise_for_status()

        # extract tge code from the location header
        redirect_uri = r.headers["Location"]
        code = redirect_uri.split("code=")[1]

        # exchange the code for the token
        r = requests.post(
            f"{self.base_url}/oauth/v2/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "http://localhost:1234",
                "client_id": client_id,
                "code_verifier": code_verifier,
            },
        )
        r.raise_for_status()
        return r.json()


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
