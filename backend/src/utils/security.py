import hashlib


def hash_password(password: str, salt: str = "") -> str:
    """
    Hache un mot de passe avec l'algorithme SHA-256.
 
    Parameters
    ----------
    password : str
        Mot de passe en clair à hacher.
    salt : str, optional
        Chaîne ajoutée au mot de passe avant le hachage, pour se
        protéger des attaques par rainbow table.
 
    Returns
    -------
    str
        Le hash résultant, sous forme hexadécimale.
    """
    password_bytes = password.encode("utf-8") + salt.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()
