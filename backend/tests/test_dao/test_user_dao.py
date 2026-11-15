from pathlib import Path

import psycopg2
import pytest

from business_object.user import User
from dao.user_dao import UserDAO
from utils.db_connection import DbConnection
from utils.settings import Settings

test_env_path = Path(__file__).resolve().parents[2] / ".test_env"


@pytest.fixture(scope="session")
def db_connection():
    """Fournit un pool de connexion à la base de données de test."""
    settings = Settings(_env_file=test_env_path if test_env_path.exists() else ".test_env")
    return DbConnection(settings)


@pytest.fixture
def user_dao(db_connection):
    return UserDAO(db_connection)


@pytest.fixture(autouse=True)
def setup_test_environment(db_connection):
    """Nettoie la table user avant chaque test."""
    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_favorite_station;")
                cur.execute('DELETE FROM "user";')
    yield
    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_favorite_station;")
                cur.execute('DELETE FROM "user";')


@pytest.fixture
def sample_users():
    """Génère une liste isolée d'objets User pour chaque test."""
    return [
        User(
            username="alice",
            password_hashed="hash_alice_123",
            email="alice@test.fr",
            role="ADMIN",
        ),
        User(
            username="bob",
            password_hashed="hash_bob_456",
            email="bob@test.fr",
            role="USER",
        ),
        User(
            username="charlie",
            password_hashed="hash_charlie_789",
            email="charlie@test.fr",
            role="USER",
        ),
    ]


@pytest.fixture
def inserted_users(user_dao, sample_users):
    """Insère les utilisateurs d'exemple en base de données et les retourne."""
    for u in sample_users:
        user_dao.create_user(u)
    return sample_users


# Tests de create_user()


def test_create_user_ok(user_dao, sample_users):
    """Création de l'utilisateur réussie"""
    # GIVEN
    user = sample_users[0]

    # WHEN
    created = user_dao.create_user(user)

    # THEN
    assert created is True
    assert isinstance(user.user_id, int)
    retrieved = user_dao.get_by_id(user.user_id)
    assert retrieved is not None
    assert retrieved.username == user.username
    assert retrieved.email == user.email
    assert retrieved.role == user.role


def test_create_user_duplicate_username_fail(user_dao, sample_users):
    """Échec lors de la création d'un utilisateur avec un nom d'utilisateur déjà existant"""
    # GIVEN
    user_dao.create_user(sample_users[0])
    duplicate_user = User(
        username=sample_users[0].username,
        password_hashed="different_hash",
        email="unique_email@test.fr",
        role="USER",
    )

    # WHEN / THEN
    with pytest.raises(psycopg2.IntegrityError):
        user_dao.create_user(duplicate_user)


# Tests de get_by_id()


def test_get_by_id_existing(user_dao, inserted_users):
    """Recherche par id de l'utilisateur réussie"""
    # GIVEN
    target_id = inserted_users[0].user_id

    # WHEN
    user = user_dao.get_by_id(target_id)

    # THEN
    assert user is not None
    assert isinstance(user, User)
    assert user.user_id == target_id
    assert user.username == inserted_users[0].username
    assert user.email == inserted_users[0].email


def test_get_by_id_non_existing(user_dao, inserted_users):
    """Recherche par id de l'utilisateur impossible car l'id n'existe pas"""
    # GIVEN
    unknown_id = 999999

    # WHEN
    user = user_dao.get_by_id(unknown_id)

    # THEN
    assert user is None


# Tests de get_by_username()


def test_get_by_username_existing(user_dao, inserted_users):
    """Recherche par le nom d'utilisateur réussie"""
    # GIVEN
    target_username = inserted_users[0].username

    # WHEN
    user = user_dao.get_by_username(target_username)

    # THEN
    assert user is not None
    assert isinstance(user, User)
    assert user.username == target_username
    assert user.email == inserted_users[0].email


def test_get_by_username_non_existing(user_dao, inserted_users):
    """Recherche par le nom d'utilisateur impossible car celui-ci n'existe pas"""
    # GIVEN
    unknown_username = "non_existent_username"

    # WHEN
    user = user_dao.get_by_username(unknown_username)

    # THEN
    assert user is None


# Tests de get_by_access_token()


def test_get_by_access_token_existing(user_dao, inserted_users):
    """Recherche par le token d'accès réussie"""
    # GIVEN
    target_user = inserted_users[0]
    token = "valid_test_access_token_123"
    user_dao.update_user(target_user.user_id, {"access_token": token})

    # WHEN
    user = user_dao.get_by_access_token(token)

    # THEN
    assert user is not None
    assert isinstance(user, User)
    assert user.user_id == target_user.user_id
    assert user.access_token == token


def test_get_by_access_token_non_existing(user_dao, inserted_users):
    """Recherche par le token d'accès impossible car celui-ci n'existe pas"""
    # GIVEN
    unknown_token = "unknown_access_token_999"

    # WHEN
    user = user_dao.get_by_access_token(unknown_token)

    # THEN
    assert user is None


# Tests de list_users()


def test_list_users_no_params(user_dao, inserted_users):
    """Retourne la liste complète des utilisateurs"""
    # WHEN
    users = user_dao.list_users()

    # THEN
    assert isinstance(users, list)
    assert len(users) == len(inserted_users)
    for u in users:
        assert isinstance(u, User)


def test_list_users_filter_role(user_dao, inserted_users):
    """Filtrage réussi des utilisateurs par rôle"""
    # WHEN
    admins = user_dao.list_users(role="ADMIN")
    standard_users = user_dao.list_users(role="USER")

    # THEN
    assert len(admins) == 1
    assert admins[0].username == "alice"
    assert len(standard_users) == 2
    assert {u.username for u in standard_users} == {"bob", "charlie"}


def test_list_users_filter_username(user_dao, inserted_users):
    """Filtrage réussi par recherche partielle insensible à la casse sur username"""
    # WHEN
    results = user_dao.list_users(username="li")  # "alice" et "charlie"

    # THEN
    assert len(results) == 2
    assert {u.username for u in results} == {"alice", "charlie"}


def test_list_users_filter_email(user_dao, inserted_users):
    """Filtrage réussi par recherche partielle insensible à la casse sur email"""
    # WHEN
    results = user_dao.list_users(email="bob@test.fr")

    # THEN
    assert len(results) == 1
    assert results[0].username == "bob"


def test_list_users_filter_is_active(user_dao, inserted_users):
    """Filtrage réussi par statut is_active"""
    # WHEN
    active_users = user_dao.list_users(is_active=True)

    # THEN
    assert len(active_users) == 3


def test_list_users_pagination(user_dao, inserted_users):
    """Pagination réussie pour list_users"""
    # WHEN
    page_1 = user_dao.list_users(limit=2, offset=0)
    page_2 = user_dao.list_users(limit=2, offset=2)

    # THEN
    assert len(page_1) == 2
    assert len(page_2) == 1
    assert page_1[0].user_id != page_2[0].user_id


def test_list_users_dict_param(user_dao, inserted_users):
    """Filtrage réussi en passant un dictionnaire de filtres dans user_id"""
    # WHEN
    results = user_dao.list_users({"role": "ADMIN"})

    # THEN
    assert len(results) == 1
    assert results[0].username == "alice"


def test_list_users_invalid_params(user_dao, inserted_users):
    """Retourne une liste vide lorsqu'un des critères n'a pas le bon format"""
    # WHEN / THEN
    assert user_dao.list_users(role="INVALID_ROLE") == []
    assert user_dao.list_users(limit=-1) == []
    assert user_dao.list_users(offset=-5) == []
    assert user_dao.list_users(user_id="not_an_int") == []


# Tests de update_user()


def test_update_user_ok(user_dao, inserted_users):
    """Mise à jour de l'utilisateur réussie"""
    # GIVEN
    target_user = inserted_users[0]
    new_email = "alice_updated@test.fr"

    # WHEN
    update_ok = user_dao.update_user(user_id=target_user.user_id, updates={"email": new_email})

    # THEN
    assert update_ok is True
    updated_user = user_dao.get_by_id(target_user.user_id)
    assert updated_user is not None
    assert updated_user.email == new_email


def test_update_user_fail_unknown_id(user_dao, inserted_users):
    """Mise à jour impossible car l'id n'est pas reconnu"""
    # GIVEN
    unknown_id = 999999

    # WHEN
    update_ok = user_dao.update_user(user_id=unknown_id, updates={"email": "new@test.fr"})

    # THEN
    assert update_ok is False


def test_update_user_fail_invalid_field(user_dao, inserted_users):
    """Mise à jour impossible car le champ à modifier est inconnu"""
    # GIVEN
    target_user = inserted_users[0]

    # WHEN
    update_ok = user_dao.update_user(user_id=target_user.user_id, updates={"invalid_field": "val"})

    # THEN
    assert update_ok is False


def test_update_user_fail_invalid_role(user_dao, inserted_users):
    """Mise à jour impossible car le rôle est invalide"""
    # GIVEN
    target_user = inserted_users[0]

    # WHEN
    update_ok = user_dao.update_user(user_id=target_user.user_id, updates={"role": "SUPERUSER"})

    # THEN
    assert update_ok is False


def test_update_user_fail_duplicate_username(user_dao, inserted_users):
    """Mise à jour impossible car le nom d'utilisateur est déjà pris par un autre utilisateur"""
    # GIVEN
    # inserted_users[0] est "alice", inserted_users[1] est "bob"
    target_user = inserted_users[1]

    # WHEN
    update_ok = user_dao.update_user(user_id=target_user.user_id, updates={"username": "alice"})

    # THEN
    assert update_ok is False


# Tests de delete_user()


def test_delete_user_ok(user_dao, inserted_users):
    """Suppression d'un utilisateur réussie"""
    # GIVEN
    target_id = inserted_users[1].user_id

    # WHEN
    delete_ok = user_dao.delete_user(target_id)

    # THEN
    assert delete_ok is True
    assert user_dao.get_by_id(target_id) is None


def test_delete_user_fail_unknown_id(user_dao, inserted_users):
    """Suppression impossible car l'utilisateur n'existe pas"""
    # GIVEN
    unknown_id = 999999

    # WHEN
    delete_ok = user_dao.delete_user(unknown_id)

    # THEN
    assert delete_ok is False


def test_delete_user_fail_invalid_id_type(user_dao, inserted_users):
    """Suppression impossible car le type d'id est invalide"""
    # WHEN / THEN
    assert user_dao.delete_user("invalid_string_id") is False
    assert user_dao.delete_user(True) is False
