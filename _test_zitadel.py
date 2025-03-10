from tests.fixtures.zitadel import ZitadelIntegration


z = ZitadelIntegration()

z.load_pat()
z.test_connectivty()
z.create_project("test")
p = z.get_project("test")
print(p)

z.create_api_app(p["id"], "test-app")

a = z.get_app(p["id"], "test-app")
print(a)

k = z.create_api_app_key(p["id"], a["id"])
print(k)

z.create_web_app(p["id"], "test-web-app")

aw = z.get_app(p["id"], "test-web-app")
print(aw)


user = z.create_user("test-user", "test")

token = z.login_user(
    username="test-user",
    password="test",
    client_id=aw["oidcConfig"]["clientId"],
)

print(token)
