from pathlib import Path

import pytest

from business_object.user import User
from dao.user_dao import UserDAO
from utils.db_connection import DbConnection
from utils.settings import Settings

test_env_path = Path(__file__).resolve().parents[2] / ".test_env"


@pytest.fixture(scope="session")
def db_connection():
    """Fournit un pool de connexion à la base de données de test."""
    settings = Settings(
        _env_file=test_env_path if test_env_path.exists() else ".test_env"
    )
    return DbConnection(settings)


@pytest.fixture
def user_dao(db_connection):
    return UserDAO(db_connection)


# Tests de create_user()

def test_create_user_ok(user_dao):
    """Création de l'utilisateur réussie"""

    # GIVEN
    user = User(
        username="myusername",
        password_hashed="averycoolpasswordtouse",
        email="myemail@email.fr",
        role="USER"
    )

    # WHEN
    created = user_dao.create_user(user)

    # THEN
    assert created
    assert user.user_id


# Tests de get_by_id()

def test_get_by_id_existing(user_dao):
    """Recherche par id de l'utilisateur réussie"""

    # GIVEN
    user_id = 2

    # WHEN
    user = user_dao.get_by_id(user_id)

    # THEN
    assert user is not None


def test_get_by_id_non_existing(user_dao):
    """Recherche par id de l'utilisateur impossible car l'id n'existe pas"""

    # GIVEN
    user_id = 1765365236

    # WHEN
    user = user_dao.get_by_id(user_id)

    # THEN
    assert user is None


# Tests de get_by_username()

def test_get_by_username_existing(user_dao):
    """Recherche par le nom d'utilisateur réussie"""

    # GIVEN
    username = "vn"

    # WHEN
    user = user_dao.get_by_username(username)

    # THEN
    assert user is not None


def test_get_by_username_non_existing(user_dao):
    """Recherche par le nom d'utilisateur impossible car celui-ci n'existe pas"""

    # GIVEN
    username = "anotherusername"

    # WHEN
    user = user_dao.get_by_username(username)

    # THEN
    assert user is None


# Tests de get_by_access_token()

def test_get_by_access_token_existing(user_dao):
    """Recherche pas le token d'accès réussie"""

    # GIVEN
    token = "accesstoken3"

    # THEN
    user = user_dao.get_by_access_token(token)

    # WHEN
    assert user is not None


def test_get_by_access_token_non_existing(user_dao):
    """Recherche pas le token d'accès impossible car celui-ci n'existe pas"""

    # GIVEN
    token = "notarandomstring"

    # THEN
    user = user_dao.get_by_access_token(token)

    # WHEN
    assert user is None


# Tests de list_users()

def test_list_users_no_params(user_dao):
    """Nous vérifions si la méthode retourne bien une liste d'objets User
    de taille supérieure à 2"""

    # WHEN
    users = user_dao.list_users()

    # THEN
    assert isinstance(users, list)
    for p in users:
        assert isinstance(p, User)
    assert len(users) >= 2


def test_list_users_with_params(user_dao):
    """Nous vérifions si la méthode retourne bien une liste d'objets User qui est filtrée
    selon le paramètre indiqué"""
    pass


# Tests de update_user()

def test_update_user_ok(user_dao):
    """Mise à jour de l'utilisateur réussie"""

    # GIVEN
    new_email = "thenewemail@email.fr"
    user_id = 2

    # WHEN
    update_ok = user_dao.update_user(user_id=user_id, updates={"email": new_email})

    # THEN
    assert update_ok


def test_update_user_fail(user_dao):
    """Mise à jour de l'utilisateur impossible car l'id n'est pas reconnu.

    La mise à jour ne fonctionne pas non plus lorsqu'un des attributs de User à
    changer n'a pas le bon type ou est le même que le précédent ou qu'il correspond
    à celui d'un autre utilisateur.
    """

    # GIVEN
    new_email = "thenewemail@email.fr"
    user_id = 156564435

    # WHEN
    update_ok = user_dao.update_user(user_id=user_id, updates={"email": new_email})

    # THEN
    assert not update_ok


# Tests de delete_user()

def test_delete_user_ok(user_dao):
    """Suppression d'un utilisateur réussie"""

    # GIVEN
    user_id = 2

    # WHEN
    delete_ok = user_dao.delete_user(user_id)

    # THEN
    assert delete_ok


def test_delete_user_fail(user_dao):
    """Suppression d'un utilisateur impossible car il n'existe pas"""

    # GIVEN
    user_id = 5645657678

    # WHEN
    delete_ok = user_dao.delete_user(user_id)

    # THEN
    assert not delete_ok
