import pytest
from app.utils.security import hash_password, verify_password, create_access_token, decode_token

def test_argon2_password_hashing():
    raw_pwd = "SuperSecretPassword2026!"
    hashed = hash_password(raw_pwd)
    assert hashed.startswith("$argon2id$")
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_jwt_token_creation_and_decoding():
    token = create_access_token(subject="sec_engineer", role="ADMIN")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "sec_engineer"
    assert payload["role"] == "ADMIN"
    assert payload["type"] == "access"

def test_invalid_token_decoding():
    assert decode_token("invalid.token.structure") is None
