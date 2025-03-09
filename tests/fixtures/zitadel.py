import pytest


@pytest.fixture
def opaque_token():
    """placeholder token"""
    return "HEFx_abcdefghijklmnopqrstuvwxyz123456789-abcdefghijklmno_AB_pqrstuvwxyz123456789abcdefghijklmnopqrstuvwx"


@pytest.fixture
def jwt_token():
    """placeholder jwt"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
