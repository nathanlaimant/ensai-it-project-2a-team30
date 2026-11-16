from unittest.mock import MagicMock

import pytest

from business_object.user import User
from dao.user_dao import UserDAO
from schema.user_model import LoginResponse, UserSearchRequest
from service.user_service import UserService
from utils.security import hash_password
from utils.token_cache import app_token_cache


@pytest.fixture
def user_dao():
    return MagicMock(spec=UserDAO)


@pytest.fixture
def user_service(user_dao):
    return UserService(user_dao)


# --- Tests de signup() ---


def test_signup_ok(user_service, user_dao):
    """L'inscription d'un nouvel utilisateur avec des données valides réussit."""
    # GIVEN
    dto = {
        "username": "testuser",
        "email": "testuser@example.org",
        "password": "SecurePassword1",
    }
    user_dao.create_user.return_value = True

    # WHEN
    result = user_service.signup(dto)

    # THEN
    assert result is True
    assert user_dao.create_user.call_count == 1
    created_user = user_dao.create_user.call_args[0][0]
    assert created_user.username == "testuser"
    assert created_user.email == "testuser@example.org"
    assert created_user.password_hashed == hash_password("SecurePassword1")
    assert created_user.role == "USER"
    assert created_user.is_active is True


def test_signup_rejects_non_dict(user_service):
    """L'inscription échoue si le payload n'est pas un dictionnaire."""
    assert user_service.signup(None) is False
    assert user_service.signup("not_a_dict") is False
    assert user_service.signup([1, 2, 3]) is False


def test_signup_rejects_blank_or_invalid_fields(user_service):
    """L'inscription échoue si des champs obligatoires sont absents, vides ou non-chaînes."""
    assert (
        user_service.signup({"username": "user", "email": "a@a.com", "password": "   "})
        is False
    )
    assert (
        user_service.signup({"username": "  ", "email": "a@a.com", "password": "pass"})
        is False
    )
    assert (
        user_service.signup({"username": "user", "email": "", "password": "pass"})
        is False
    )
    assert user_service.signup({"username": "user", "password": "pass"}) is False
    assert (
        user_service.signup({"username": 123, "email": "a@a.com", "password": "pass"})
        is False
    )


def test_signup_dao_failure(user_service, user_dao):
    """L'inscription échoue si le DAO ne parvient pas à créer l'utilisateur."""
    dto = {"username": "user", "email": "a@a.com", "password": "password"}
    user_dao.create_user.return_value = False

    assert user_service.signup(dto) is False


# --- Tests de login() ---


def test_login_ok(user_service, user_dao):
    """Connexion réussie avec des identifiants valides."""
    # GIVEN
    pwd_hash = hash_password("Secret123")
    user = User(
        user_id=42,
        username="alice",
        password_hashed=pwd_hash,
        email="alice@test.fr",
        role="ADMIN",
        is_active=True,
    )
    user_dao.get_by_username.return_value = user
    user_dao.update_user.return_value = True

    # WHEN
    response = user_service.login("alice", pwd_hash)

    # THEN
    assert isinstance(response, LoginResponse)
    assert response.user_id == 42
    assert response.username == "alice"
    assert bool(response.access_token)
    user_dao.update_user.assert_called_once_with(
        42, {"access_token": response.access_token}
    )
    assert app_token_cache.get(response.access_token) == (42, "ADMIN")


def test_login_wrong_password(user_service, user_dao):
    """Connexion rejetée si le mot de passe ne correspond pas."""
    user = User(
        user_id=1,
        username="bob",
        password_hashed="correct_hash",
        email="bob@test.fr",
        role="USER",
        is_active=True,
    )
    user_dao.get_by_username.return_value = user

    assert user_service.login("bob", "wrong_hash") is None


def test_login_unknown_user(user_service, user_dao):
    """Connexion rejetée si l'utilisateur n'existe pas."""
    user_dao.get_by_username.return_value = None
    assert user_service.login("ghost", "hash") is None


def test_login_inactive_user(user_service, user_dao):
    """Connexion rejetée si l'utilisateur est inactif."""
    pwd_hash = "some_hash"
    user = User(
        user_id=2,
        username="disabled",
        password_hashed=pwd_hash,
        email="d@test.fr",
        role="USER",
        is_active=False,
    )
    user_dao.get_by_username.return_value = user

    assert user_service.login("disabled", pwd_hash) is None


def test_login_missing_user_id(user_service, user_dao):
    """Connexion rejetée si l'utilisateur n'a pas d'identifiant valide."""
    pwd_hash = "some_hash"
    user = User(
        user_id=None,
        username="noid",
        password_hashed=pwd_hash,
        email="n@test.fr",
        role="USER",
        is_active=True,
    )
    user_dao.get_by_username.return_value = user

    assert user_service.login("noid", pwd_hash) is None


def test_login_invalid_argument_types(user_service):
    """Connexion rejetée si les types d'arguments ne sont pas des chaînes."""
    assert user_service.login(123, "hash") is None
    assert user_service.login("user", None) is None


def test_login_update_user_fails(user_service, user_dao):
    """Connexion rejetée si la mise à jour du token en base échoue."""
    pwd_hash = "hash"
    user = User(
        user_id=5,
        username="fail_update",
        password_hashed=pwd_hash,
        email="f@test.fr",
        role="USER",
        is_active=True,
    )
    user_dao.get_by_username.return_value = user
    user_dao.update_user.return_value = False

    assert user_service.login("fail_update", pwd_hash) is None


# --- Tests de logout() ---


def test_logout_ok(user_service, user_dao):
    """Déconnexion réussie effaçant le token en base et en cache."""
    # GIVEN
    user = User(
        user_id=10,
        username="user10",
        password_hashed="h",
        email="u@test.fr",
        role="USER",
        access_token="active_token_123",
    )
    app_token_cache.set("active_token_123", (10, "USER"))
    user_dao.get_by_id.return_value = user
    user_dao.update_user.return_value = True

    # WHEN
    result = user_service.logout(10)

    # THEN
    assert result is True
    user_dao.update_user.assert_called_once_with(10, {"access_token": None})
    assert app_token_cache.get("active_token_123") is None


def test_logout_ok_without_previous_token(user_service, user_dao):
    """Déconnexion réussie lorsque l'utilisateur n'avait pas de token."""
    user = User(
        user_id=11,
        username="user11",
        password_hashed="h",
        email="u11@test.fr",
        role="USER",
        access_token="",
    )
    user_dao.get_by_id.return_value = user
    user_dao.update_user.return_value = True

    assert user_service.logout(11) is True


def test_logout_unknown_user(user_service, user_dao):
    """Déconnexion échoue si l'utilisateur n'existe pas."""
    user_dao.get_by_id.return_value = None
    assert user_service.logout(999) is False


def test_logout_invalid_user_id_types(user_service):
    """Déconnexion échoue si user_id n'est pas un entier valide."""
    assert user_service.logout("not_an_int") is False
    assert user_service.logout(True) is False
    assert user_service.logout(None) is False


def test_logout_update_fails(user_service, user_dao):
    """Déconnexion échoue si update_user échoue."""
    user = User(
        user_id=12,
        username="u12",
        password_hashed="h",
        email="u12@test.fr",
        role="USER",
    )
    user_dao.get_by_id.return_value = user
    user_dao.update_user.return_value = False

    assert user_service.logout(12) is False


# --- Tests de get_user_by_id() ---


def test_get_user_by_id(user_service, user_dao):
    """Récupère l'utilisateur par ID via le DAO."""
    user = User(
        user_id=1,
        username="alice",
        password_hashed="h",
        email="a@test.fr",
        role="USER",
    )
    user_dao.get_by_id.return_value = user

    assert user_service.get_user_by_id(1) == user
    user_dao.get_by_id.assert_called_once_with(1)


# --- Tests de list_users() ---


def test_list_users(user_service, user_dao):
    """Transmission correcte des filtres et pagination de UserSearchRequest au DAO."""
    # GIVEN
    req = UserSearchRequest(
        user_id=5,
        username="ali",
        email="ali@test.fr",
        role="ADMIN",
        is_active=True,
        page=3,
        size=20,
    )
    mock_users = [
        User(
            user_id=5,
            username="ali",
            password_hashed="h",
            email="ali@test.fr",
            role="ADMIN",
        )
    ]
    user_dao.list_users.return_value = mock_users

    # WHEN
    result = user_service.list_users(req)

    # THEN
    assert result == mock_users
    user_dao.list_users.assert_called_once_with(
        user_id=5,
        username="ali",
        email="ali@test.fr",
        role="ADMIN",
        is_active=True,
        limit=20,
        offset=40,
    )


# --- Tests de update_user() ---


def test_update_user(user_service, user_dao):
    """Transmission de la mise à jour au DAO."""
    user_dao.update_user.return_value = True
    assert user_service.update_user(1, {"email": "new@test.fr"}) is True
    user_dao.update_user.assert_called_once_with(1, {"email": "new@test.fr"})


# --- Tests de delete_user() ---


def test_delete_user(user_service, user_dao):
    """Transmission de la suppression au DAO."""
    user_dao.delete_user.return_value = True
    assert user_service.delete_user(1) is True
    user_dao.delete_user.assert_called_once_with(1)
