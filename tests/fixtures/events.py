import pytest


def event_template():
    return {
        "version": "2.0",
        "type": "REQUEST",
        "routeArn": "arn:aws:execute-api:eu-central-1:651706778841:cghnha20c0/$default/GET/private",
        "identitySource": [],
        "routeKey": "GET /private",
        "rawPath": "/private",
        "rawQueryString": "",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "cache-control": "no-cache",
            "content-length": "0",
            "host": "cghnha20c0.execute-api.eu-central-1.amazonaws.com",
            "postman-token": "994b264e-e477-4ec1-bbe4-a2805a59381e",
            "user-agent": "PostmanRuntime/7.43.0",
            "x-amzn-trace-id": "Root=1-67cd1e3c-7de81d25544b229e160183b1",
            "x-forwarded-for": "81.6.47.76",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https",
        },
        "requestContext": {
            "accountId": "651706778841",
            "apiId": "cghnha20c0",
            "domainName": "cghnha20c0.execute-api.eu-central-1.amazonaws.com",
            "domainPrefix": "cghnha20c0",
            "http": {
                "method": "GET",
                "path": "/private",
                "protocol": "HTTP/1.1",
                "sourceIp": "81.6.47.76",
                "userAgent": "PostmanRuntime/7.43.0",
            },
            "requestId": "HJGpjhW0liAEP4g=",
            "routeKey": "GET /private",
            "stage": "$default",
            "time": "09/Mar/2025:04:51:08 +0000",
            "timeEpoch": 1741495868796,
        },
    }


@pytest.fixture
def event_without_authorization():
    return event_template()


@pytest.fixture
def event_with_token(opaque_token):
    event = event_template()

    event["identitySource"] = [
        f"Bearer {opaque_token}",
    ]
    event["headers"]["authorization"] = (f"Bearer {opaque_token}",)

    return event
