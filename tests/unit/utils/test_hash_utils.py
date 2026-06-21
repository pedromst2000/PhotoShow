"""
Unit tests for the hash_password utility.
"""

import bcrypt

from app.utils.hash_utils import hash_password


class TestHashPassword:
    def test_returns_string(self):
        result = hash_password("Test1_abc")
        assert isinstance(result, str)

    def test_produces_valid_bcrypt_hash(self):
        """Output must begin with a recognised bcrypt prefix."""
        result = hash_password("Test1_abc")
        assert result.startswith(("$2b$", "$2a$"))

    def test_different_hash_each_call(self):
        """bcrypt uses a random salt — the same input produces different outputs."""
        h1 = hash_password("Test1_abc")
        h2 = hash_password("Test1_abc")
        assert h1 != h2

    def test_hash_is_verifiable_with_bcrypt(self):
        """The output must be verifiable by bcrypt.checkpw."""
        plaintext = "Test1_abc"
        hashed = hash_password(plaintext)
        assert bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))

    def test_wrong_password_does_not_verify(self):
        """A different plaintext must *not* verify against the hash."""
        hashed = hash_password("Test1_abc")
        assert not bcrypt.checkpw("Wrong1_abc".encode("utf-8"), hashed.encode("utf-8"))
