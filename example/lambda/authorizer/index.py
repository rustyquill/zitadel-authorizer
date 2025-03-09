from zitadel_authorizer import Authorizer


def handler(event, context):

    authorizer = Authorizer(event)

    response = {
        "isAuthorized": True,
        "context": {
            "stringKey": "value",
            "numberKey": 1,
            "booleanKey": True,
            "arrayKey": ["value1", "value2"],
            "mapKey": {"value1": "value2"},
        },
    }

    return response
