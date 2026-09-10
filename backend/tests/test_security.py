from app.core.security import hash_password, verify_password

def test_password_hash_is_not_plaintext():
    encoded = hash_password("Password123!")
    assert encoded != "Password123!"
    assert verify_password("Password123!", encoded)
    assert not verify_password("wrong", encoded)
