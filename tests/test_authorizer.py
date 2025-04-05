def test_authorizer(
    introspection_response_bearer_no_grants, introspection_response_bearer_with_grants
):
    from zitadel_authorizer.authorizer import Authorizer
    from zitadel_authorizer.models import IntrospectionResponse

    unauthenticated = IntrospectionResponse(active=False)
    no_grants = IntrospectionResponse(**introspection_response_bearer_no_grants)
    with_grants = IntrospectionResponse(**introspection_response_bearer_with_grants)

    authorizer = Authorizer()
    assert authorizer.required_scopes == []
    assert authorizer.required_roles == []

    assert authorizer.is_authorized(unauthenticated) is False
    assert authorizer.is_authorized(no_grants) is True
    assert authorizer.is_authorized(with_grants) is True

    authorizer = Authorizer(required_scopes=["openid", "profile", "email"])
    assert authorizer.is_authorized(unauthenticated) is False
    assert authorizer.is_authorized(no_grants) is True
    assert authorizer.is_authorized(with_grants) is True

    authorizer = Authorizer(required_scopes=["openid", "profile", "email", "offline"])
    assert authorizer.is_authorized(unauthenticated) is False
    assert authorizer.is_authorized(no_grants) is False
    assert authorizer.is_authorized(with_grants) is False

    authorizer = Authorizer(required_roles=["USER", "ADMIN"])
    assert authorizer.is_authorized(unauthenticated) is False
    assert authorizer.is_authorized(no_grants) is False
    assert authorizer.is_authorized(with_grants) is True

    authorizer = Authorizer(required_roles=["USER", "ADMIN", "WRITER"])
    assert authorizer.is_authorized(unauthenticated) is False
    assert authorizer.is_authorized(no_grants) is False
    assert authorizer.is_authorized(with_grants) is False
