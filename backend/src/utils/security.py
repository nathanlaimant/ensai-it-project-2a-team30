import hashlib


def hash_password(password: str, salt: str = "") -> str:
    """Hashes a password using the SHA-256 algorithm.
    Args:
        password (str): The plain text password to be hashed.
        salt (str, optional): A string added to the password before hashing
            to protect against rainbow table attacks.
    Returns:
        str: The resulting hexadecimal hash string.
    """
    password_bytes = password.encode("utf-8") + salt.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()
