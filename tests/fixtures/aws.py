import pytest
import boto3
import os
from moto import mock_aws
import json


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def ssm(aws_credentials):
    """
    Return a mocked ssm client
    """
    with mock_aws():
        yield boto3.client("ssm", region_name="us-east-1")


@pytest.fixture()
def aws_api_gateway_proxy_event_no_authorizer():
    return json.loads(
        """{
        "version": "2.0",
        "routeKey": "GET /public/{proxy+}",
        "rawPath": "/public/anyone",
        "rawQueryString": "",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "content-length": "0",
            "host": "localhost.execute-api.eu-central-1.amazonaws.com",
            "postman-token": "63277574-c5da-4dc0-8449-12252475ed4d",
            "user-agent": "PostmanRuntime/7.43.3",
            "x-amzn-trace-id": "Root=1-67f234d1-1936e6d7600077121ec6f587",
            "x-forwarded-for": "127.0.0.1",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https"
        },
        "requestContext": {
            "accountId": "651706778841",
            "apiId": "localhost",
            "domainName": "localhost.execute-api.eu-central-1.amazonaws.com",
            "domainPrefix": "localhost",
            "http": {
                "method": "GET",
                "path": "/public/anyone",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "PostmanRuntime/7.43.3"
            },
            "requestId": "Il0wwjtZliAEJmQ=",
            "routeKey": "GET /public/{proxy+}",
            "stage": "$default",
            "time": "06/Apr/2025:08:01:21 +0000",
            "timeEpoch": 1743926481222
        },
        "pathParameters": {"proxy": "anyone"},
        "isBase64Encoded": false
    }"""
    )


@pytest.fixture()
def aws_api_gateway_proxy_event_with_authorizer():
    return json.loads(
        """{
        "version": "2.0",
        "routeKey": "GET /private/{proxy+}",
        "rawPath": "/private/anyone",
        "rawQueryString": "",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "authorization": "Bearer abcdefghijklmnopqrstuvwxyz",
            "content-length": "0",
            "host": "localhost.execute-api.eu-central-1.amazonaws.com",
            "postman-token": "a8396b44-9ce5-4c0e-92e7-922e3b6871ed",
            "user-agent": "PostmanRuntime/7.43.3",
            "x-amzn-trace-id": "Root=1-67f234ca-3e8e98842478b554371de2a1",
            "x-forwarded-for": "127.0.0.1",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https"
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "localhost",
            "authorizer": {
                "lambda": {
                    "active": true,
                    "amr": null,
                    "aud": [
                        "test83920485739485",
                        "test47583920194857",
                        "test92837465019283",
                        "test38475692038475",
                        "test19283746509128"
                    ],
                    "auth_time": 1743872057,
                    "client_id": "test83920485739485",
                    "email": "test@localhost",
                    "email_verified": true,
                    "exp": 1743969145,
                    "family_name": "Test",
                    "given_name": "User",
                    "iat": 1743925945,
                    "iss": "http://localhost:8080",
                    "jti": "V2_123456789012345678-at_123456789012345678",
                    "locale": "en",
                    "name": "Test User",
                    "nbf": 1743925945,
                    "nickname": null,
                    "preferred_username": "test@localhost",
                    "project_roles": ["example"],
                    "scope": "profile email openid urn:zitadel:iam:org:project:id:zitadel:aud",
                    "sub": "278799193194145252",
                    "token_type": "Bearer",
                    "updated_at": 1722673268,
                    "username": "test@localhost"
                }
            },
            "domainName": "localhost.execute-api.eu-central-1.amazonaws.com",
            "domainPrefix": "localhost",
            "http": {
                "method": "GET",
                "path": "/private/anyone",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "PostmanRuntime/7.43.3"
            },
            "requestId": "Il0vqjQoFiAEJxg=",
            "routeKey": "GET /private/{proxy+}",
            "stage": "$default",
            "time": "06/Apr/2025:08:01:14 +0000",
            "timeEpoch": 1743926474202
        },
        "pathParameters": {"proxy": "anyone"},
        "isBase64Encoded": false
    }"""
    )
