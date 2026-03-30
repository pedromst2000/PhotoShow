import bcrypt


def hash_password(plaintext: str) -> str:
    """
    Hash a plaintext password using bcrypt and return the encoded string.

    Args:
        plaintext: The plaintext password to be hashed.

    Returns:
        str: The bcrypt-hashed password as a UTF-8 string.

    """
    return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
