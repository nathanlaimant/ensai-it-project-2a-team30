from datetime import datetime, timezone

import psycopg2
import pytest

from pathlib import Path


from business_object.user import User
from dao.user_dao import UserDAO
from utils.db_connection import DbConnection
from utils.settings import Settings
from service.user_service import UserService
from utils.security import hash_password
from business_object.station_information import StationInformation


test_env_path = Path(__file__).resolve().parents[1] / ".test_env"


@pytest.fixture(scope="session")
def db_connection():
    """Fournit un pool de connexions vers le schéma de test PostgreSQL."""
    settings = Settings(_env_file=".test_env")
    return DbConnection(settings)


@pytest.fixture
def user_service(db_connection):
    """Retourne un UserService utilisant le vrai UserDAO de test."""
    return UserService(db_connection)


def test_signup(user_service, user_dao):
    """L'inscription d'un nouvel utilisateur avec des données valides réussit."""

    # GIVEN
    username = "testuser"
    dto = {
        "username": username,
        "email": f"{username}@example.org",
        "password": "SecurePass1",
    }

    # WHEN
    result = user_service.signup(dto)

    # THEN
    assert result is True
    user = user_dao.get_by_username(username)
    assert user is not None
    assert user.username == username


def test_signup_rejects_blank_password(user_service, user_dao):
    """L'inscription échoue si le mot de passe est vide ou composé uniquement d'espaces."""

    # GIVEN
    dto = {
        "username": "testuser",
        "email": "blank@example.org",
        "password": "   ",
    }

    # WHEN
    result = user_service.signup(dto)

    # THEN
    assert result is False


def test_signup_rejects_missing_field(user_service):
    """L'inscription échoue si un champ obligatoire est absent."""

    # GIVEN
    dto = {
        "username": "testuser",
        # email manquant
        "password": "SecureP@ss1",
    }

    # WHEN
    result = user_service.signup(dto)

    # THEN
    assert result is False


def test_login_rejects_wrong_password(user_service):
    """La connexion échoue si le mot de passe haché ne correspond pas."""

    # GIVEN
    username = "testuser"
    password = "SecurePPass1"
    user_service.signup(
        {"username": username, "email": f"{username}@example.org", "password": password}
    )

    # WHEN
    login_response = user_service.login(username, wrong_password_hashed)

    # THEN
    assert login_response is None


def test_logout_ok(user_service, user_dao):
    """La déconnexion réussit et efface le token d'accès en base."""

    # GIVEN
    username = "testuser"
    password = "SecurePPass1"
    user_service.signup(
        {"username": username, "email": f"{username}@example.org", "password": password}
    )
    login_response = user_service.login(username, hash_password(password))
    assert login_response is not None

    user_id = login_response.user_id

    # WHEN
    result = user_service.logout(user_id)

    # THEN
    assert result is True


def test_logout_fails_for_unknown_user(user_service):
    """La déconnexion échoue si l'identifiant utilisateur n'existe pas en base."""

    # GIVEN
    user_id = 9_999_999

    # WHEN
    result = user_service.logout(user_id)

    # THEN
    assert result is False


def test_logout_rejects_invalid_id_type(user_service):
    """La déconnexion échoue si l'identifiant n'est pas un entier valide."""

    # GIVEN
    user_id = "int"

    # WHEN
    result = user_service.logout(user_id)

    # THEN
    assert result is False


def test_list_users_filter_by_username(user_service, user_dao):
    """list_users filtré par username retourne uniquement l'utilisateur correspondant."""

    # GIVEN –
    username = "testuser"
    user_service.signup(
        {
            "username": username,
            "email": f"{username}@example.org",
            "password": "SecurePPass1",
        }
    )

    # WHEN
    users = user_service.list_users({"username": username})

    # THEN
    assert len(users) == 1


def test_update_user_ok(user_service, user_dao):
    """La mise à jour d'un utilisateur existant avec des données valides réussit."""

    # GIVEN
    username = "testuser"
    user_service.signup(
        {
            "username": username,
            "email": f"{username}@example.org",
            "password": "SecureP@ss1",
        }
    )
    user = user_dao.get_by_username(username)
    new_email = f"updated_{username}@example.org"

    # WHEN
    result = user_service.update_user(user.user_id, {"email": new_email})

    # THEN
    assert result is True


def test_update_user_fails_for_unknown_id(user_service):
    """La mise à jour échoue si l'identifiant utilisateur n'existe pas en base."""

    # GIVEN
    user_id = 9_999_998
    updates = {"email": "ghost@example.org"}

    # WHEN
    result = user_service.update_user(user_id, updates)

    # THEN
    assert result is False
