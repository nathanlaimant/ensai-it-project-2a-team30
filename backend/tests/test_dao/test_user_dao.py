import os
from unittest.mock import patch

import psycopg2
import pytest
from business_object.user import User
from dao.user_dao import UserDao
from utils.reset_database import ResetDatabase


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation de la base de données pour les tests"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


# Tests de signup()

def test_signup_ok():
    """Création de l'utilisateur réussie"""

    # GIVEN
    user = User(username="myusername", password="averycoolpasswordtouse", email="myemail@email.fr")

    # WHEN
    creation_ok = UserDao().create(user)

    # THEN
    assert creation_ok
    assert user.user_id


def test_signup_fail():
    """Echec de la création de l'utilisateur car UserDao().create retourne False"""

    # GIVEN
    user = User(username=123, password="averycoolpasswordtouse", email="myemail@email.fr")

    # WHEN / THEN
    with pytest.raises(psycopg2.Error):
        UserDao().create(user)


# Tests de get_by_id()

def test_get_by_id_existing():
    """Recherche par id de l'utilisateur réussie"""

    # GIVEN
    user_id = 1

    # WHEN
    user = UserDao().get_by_id(user_id)

    # THEN
    assert user is not None


def test_get_by_id_non_existing():
    """Recherche par id de l'utilisateur impossible car l'id n'existe pas"""

    # GIVEN
    user_id = 1765365236

    # WHEN
    user = UserDao().get_by_id(user_id)

    # THEN
    assert user is None


# Tests de get_by_username()

def test_get_by_username_existing():
    """Recherche par le nom d'utilisateur réussie"""

    # GIVEN
    username = "vn"

    # WHEN
    user = UserDao().get_by_username(username)

    # THEN
    assert user is not None


def test_get_by_username_non_existing():
    """Recherche par le nom d'utilisateur impossible car celui-ci n'existe pas"""

    # GIVEN
    username = "anotherusername"

    # WHEN
    user = UserDao().get_by_username(username)

    # THEN
    assert user is None


# Tests de get_by_access_token()

def test_get_by_access_token_existing():
    """Recherche pas le token d'accès réussie"""

    # GIVEN
    token = "arandomstring"

    # THEN
    user = UserDao().get_by_access_token(token)

    # WHEN
    assert user is not None


def test_get_by_access_token_non_existing():
    """Recherche pas le token d'accès impossible car celui-ci n'existe pas"""

    # GIVEN
    token = "notarandomstring"

    # THEN
    user = UserDao().get_by_access_token(token)

    # WHEN
    assert user is None


# Test de list_users()

def test_list_users():
    """Nous vérifions si la méthode retourne bien une liste d'objets User
    de taille supérieure à 2"""

    # WHEN
    users = UserDao().list_users()

    # THEN
    assert isinstance(users, list)
    for p in users:
        assert isinstance(p, User)
    assert len(users) >= 2


# Tests de update_user()

def test_update_user_ok():
    """Mise à jour de l'utilisateur réussie"""

    # GIVEN
    new_email = "thenewemail@email.fr"
    user_id = 2

    # WHEN
    update_ok = UserDao().update_user(user_id=user_id, updates={"email": new_email})

    # THEN
    assert update_ok


def test_update_user_fail():
    """Mise à jour de l'utilisateur impossible car l'id n'est pas reconnu.
    
    La mise à jour ne fonctionne pas non plus lorsqu'un des attributs de User à
    changer n'a pas le bon type ou est le même que le précédent ou qu'il correspond
    à celui d'un autre utilisateur.
    """

    # GIVEN
    new_email = "thenewemail@email.fr"
    user_id = 156564435

    # WHEN
    update_ok = UserDao().update_user(user_id=user_id, updates={"email": new_email})

    # THEN
    assert not update_ok


# Tests de delete_user()

def test_delete_user_ok():
    """Suppression d'un utilisateur réussie"""

    # GIVEN
    user = User(username="myusername", password="averycoolpasswordtouse", email="myemail@email.fr")

    # WHEN
    delete_ok = UserDao().delete_user(user)

    # THEN
    assert delete_ok


def test_delete_user_fail():
    """Suppression d'un utilisateur impossible car il n'existe pas"""

    # GIVEN
    user = User(username="nousername", password="averycoolpasswordtouse", email="myemail@email.fr")

    # WHEN
    delete_ok = UserDao().delete_user(user)

    # THEN
    assert not delete_ok
