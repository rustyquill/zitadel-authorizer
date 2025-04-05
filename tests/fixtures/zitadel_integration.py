import time
import requests
from typing import List
from pydantic import BaseModel, Field


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
        for result in r.json().get("result", []):
            if result["name"] == name:
                return result

        return None

    def get_app(self, project_id: str, name: str):
        r = self.session.post(
            f"{self.base_url}/management/v1/projects/{project_id}/apps/_search"
        )
        for result in r.json().get("result", []):
            if result["name"] == name:
                return result

        return None

    def get_user(self, user_name: str):
        r = self.session.post(
            f"{self.base_url}/v2/users",
            json=dict(
                queries=[
                    dict(
                        userNameQuery=dict(
                            userName=user_name,
                            method="TEXT_QUERY_METHOD_EQUALS",
                        ),
                    )
                ],
            ),
        )
        return r.json().get("result", [{}])[0]

    def create_project(
        self,
        name: str,
        project_role_assertion: bool = False,
        project_role_check: bool = False,
        has_project_check: bool = False,
        private_label_setting: str = "PRIVATE_LABELING_SETTING_UNSPECIFIED",
    ):

        # check if the project already exists
        project = self.get_project(name)
        if project:
            return project

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
        r.raise_for_status()

        # get the full project details
        return self.get_project(name)

    def create_project_roles(self, project_id: str, roles: List[str]):
        for role in roles:
            r = self.session.post(
                f"{self.base_url}/management/v1/projects/{project_id}/roles",
                json={
                    "roleKey": role,
                    "displayName": role,
                },
            )
            if r.status_code not in [200, 409]:
                r.raise_for_status()

    def create_api_app(self, project_id: str, name: str):
        # check if the app already exists
        app = self.get_app(project_id, name)
        if app:
            return app

        r = self.session.post(
            f"{self.base_url}/management/v1/projects/{project_id}/apps/api",
            json={
                "name": name,
                "authMethodType": "API_AUTH_METHOD_TYPE_PRIVATE_KEY_JWT",
            },
        )
        r.raise_for_status()

        # get the full app details
        return self.get_app(project_id, name)

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

    def create_web_app(
        self,
        project_id: str,
        name: str,
        access_token_type: str,
        access_token_role_assertion: bool = False,
        id_token_role_assertion: bool = False,
        id_token_userinfo_assertion: bool = False,
    ):
        app = self.get_app(project_id, name)
        if app:
            return app

        r = self.session.post(
            f"{self.base_url}/management/v1/projects/{project_id}/apps/oidc",
            json={
                "name": name,
                "responseTypes": ["OIDC_RESPONSE_TYPE_CODE"],
                "grantTypes": [
                    "OIDC_GRANT_TYPE_AUTHORIZATION_CODE",
                    "OIDC_GRANT_TYPE_REFRESH_TOKEN",
                ],
                "redirectUris": ["http://localhost:1234"],
                "appType": "OIDC_APP_TYPE_WEB",
                "authMethodType": "OIDC_AUTH_METHOD_TYPE_NONE",
                "accessTokenType": access_token_type,
                "accessTokenRoleAssertion": access_token_role_assertion,
                "idTokenRoleAssertion": id_token_role_assertion,
                "idTokenUserinfoAssertion": id_token_userinfo_assertion,
                "devMode": True,
            },
        )
        r.raise_for_status()

        # get the full app details
        return self.get_app(project_id, name)

    def create_user(self, username: str, password: str):

        # check if the user already exists
        user = self.get_user(username)
        if user:
            return user

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
        r.raise_for_status()

        # skip mfa
        user_id = r.json().get("userId")
        r = self.session.post(
            url=f"{self.base_url}/v2/users/{user_id}/mfa_init_skipped", json={}
        )
        # get all user details
        return self.get_user(username)

    def _get_gorilla_csrf_token(self, html: str):
        """parses the html output for the csrf token"""

        # parse the login page for the gorilla crsf token
        # <input type="hidden" name="gorilla.csrf.Token" value="d7vfg2exNvgkdP/pDCHXX4RXAaKIyn0SLChublQfU6SQC2TZ5vMD5R2S6SHPlD2o1gfIGlqo8xLKjdnUjELrJA==">
        for line in html.split("\n"):
            if "gorilla.csrf.Token" in line:
                return line.split('value="')[1].split('"')[0]

        return None

    def _authorize(self, client_id: str, code_challenge: str):
        """call the authorize endpoint and return the reuest id and the zitadel user agent cookie and the next login url"""

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
        login_url = f"{self.base_url}{r.headers['Location']}"

        return request_id, zitadel_user_agent, login_url

    def _login(self, login_url: str, zitadel_user_agent: str):
        """call the login endpoint to retrieve the zitadel login csrf token and the gorilla csrf token"""

        # navigate to the login page to get the crsf token and crsf cookie
        r = requests.get(
            login_url,
            allow_redirects=False,
            cookies={"zitadel.useragent": zitadel_user_agent},
        )
        r.raise_for_status()

        # get the zitadel csrf cookie
        zitadel_login_csrf = r.cookies.get_dict().get("zitadel.login.csrf")
        gorilla_csrf_token = self._get_gorilla_csrf_token(r.text)

        return zitadel_login_csrf, gorilla_csrf_token

    def _authorize_redirect(
        self, authorize_url: str, zitadel_user_agent: str, zitadel_login_csrf: str
    ):
        """call the authorize endpoint with the received redirect to lease the token"""

        # finally call the authorize endpoint with the request id to receive the token code
        r = requests.get(
            url=authorize_url,
            allow_redirects=False,
            cookies={
                "zitadel.useragent": zitadel_user_agent,
                "zitadel.login.csrf": zitadel_login_csrf,
            },
        )
        r.raise_for_status()

        # extract tge code from the location header
        code = r.headers["Location"].split("code=")[1]

        return code

    def _loginname(
        self,
        gorilla_csrf_token: str,
        request_id: str,
        username: str,
        zitadel_user_agent: str,
        zitadel_login_csrf: str,
    ):
        """call the loginname endpoint, this is required to not raise "is not human" errors"""

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
        return self._get_gorilla_csrf_token(r.text)

    def _password(
        self,
        gorilla_csrf_token: str,
        request_id: str,
        username: str,
        password: str,
        zitadel_user_agent: str,
        zitadel_login_csrf: str,
    ):
        """call the password endpoint to retrieve the authorize redirect to lease the token"""

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

        return r.headers["Location"]

    def _token(self, code: str, client_id: str, code_verifier: str):
        """exchange the code for the token"""
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

    def login_user(self, username: str, password: str, client_id: str):

        code_verifier, code_challenge = pkce.generate_pkce_pair()
        request_id, zitadel_user_agent, login_url = self._authorize(
            client_id=client_id, code_challenge=code_challenge
        )
        zitadel_login_csrf, gorilla_csrf_token = self._login(
            login_url=login_url, zitadel_user_agent=zitadel_user_agent
        )
        gorilla_csrf_token = self._loginname(
            gorilla_csrf_token=gorilla_csrf_token,
            request_id=request_id,
            username=username,
            zitadel_user_agent=zitadel_user_agent,
            zitadel_login_csrf=zitadel_login_csrf,
        )
        authorize_url = self._password(
            gorilla_csrf_token=gorilla_csrf_token,
            request_id=request_id,
            username=username,
            password=password,
            zitadel_user_agent=zitadel_user_agent,
            zitadel_login_csrf=zitadel_login_csrf,
        )
        code = self._authorize_redirect(
            authorize_url=authorize_url,
            zitadel_user_agent=zitadel_user_agent,
            zitadel_login_csrf=zitadel_login_csrf,
        )

        token = self._token(code=code, client_id=client_id, code_verifier=code_verifier)
        return token


class ZitadelUrls:
    issuer_url: str = "http://localhost:8080"
    introspection_endpoint: str = "http://localhost:8080/oauth/v2/introspect"


class ZitadelProject(BaseModel):
    id: str
    name: str


class ZitadelApp(BaseModel):
    id: str
    name: str


class ZitadelApiApp(ZitadelApp):
    api_config: dict = Field(alias="apiConfig")

    @property
    def client_id(self):
        return self.api_config["clientId"]


class ZitadelWebapp(ZitadelApp):
    oidc_config: dict = Field(alias="oidcConfig")

    @property
    def client_id(self):
        return self.oidc_config["clientId"]


class ZitadelApiAppKey(BaseModel):
    id: str
    key_details: str = Field(alias="keyDetails")


class ZitadelToken(BaseModel):
    id_token: str = "unauthorized"
    access_token: str = "unauthorized"


class ZitadelUser(BaseModel):
    id: str = Field(alias="userId")
    username: str
    password: str
