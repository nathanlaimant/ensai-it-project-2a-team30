from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

import service.user_service as user_service_module
from business_object.user import User
from dao.user_dao import UserDAO
from service.user_service import UserService
from utils.security import hash_password


@pytest.fixture
def user_dao():
    return MagicMock(spec=UserDAO)


@pytest.fixture
def service(user_dao):
    return UserService(user_dao)


def make_user(**overrides):
    values = {
        "user_id": 7,
        "username": "alice",
        "password_hashed": hash_password("secret"),
        "email": "alice@example.org",
        "role": "USER",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "access_token": "old-token",
    }
    values.update(overrides)
    return User(**values)


def test_signup_hashes_password_and_creates_regular_user(service, user_dao):
    user_dao.create_user.return_value = True

    assert service.signup(
        {"username": " alice ", "email": " alice@example.org ", "password": "secret"}
    )

    created_user = user_dao.create_user.call_args.args[0]
    assert created_user.username == "alice"
    assert created_user.email == "alice@example.org"
    assert created_user.password_hashed == hash_password("secret")
    assert created_user.role == "USER"
    assert created_user.is_active


@pytest.mark.parametrize(
    "dto",
    [None, {}, {"username": "alice", "email": "alice@example.org", "password": " "}],
)
def test_signup_rejects_invalid_data(service, user_dao, dto):
    assert service.signup(dto) is False
    user_dao.create_user.assert_not_called()


def test_login_persists_token_and_caches_user(service, user_dao):
    user = make_user()
    user_dao.get_by_username.return_value = user
    user_dao.update_user.return_value = True

    with (
        patch.object(user_service_module, "generate_user_token", return_value="new-token"),
        patch.object(user_service_module, "app_token_cache") as token_cache,
    ):
        assert service.login("alice", hash_password("secret")) == "new-token"

    user_dao.update_user.assert_called_once_with(7, {"access_token": "new-token"})
    token_cache.set.assert_called_once_with("new-token", (7, "USER"))


@pytest.mark.parametrize(
    "user, password_hashed",
    [
        (None, hash_password("secret")),
        (make_user(is_active=False), hash_password("secret")),
        (make_user(), hash_password("incorrect")),
    ],
)
def test_login_rejects_unknown_inactive_or_wrong_password(
    service, user_dao, user, password_hashed
):
    user_dao.get_by_username.return_value = user

    assert service.login("alice", password_hashed) is None
    user_dao.update_user.assert_not_called()


def test_login_returns_none_when_token_cannot_be_persisted(service, user_dao):
    user_dao.get_by_username.return_value = make_user()
    user_dao.update_user.return_value = False

    with (
        patch.object(user_service_module, "generate_user_token", return_value="new-token"),
        patch.object(user_service_module, "app_token_cache") as token_cache,
    ):
        assert service.login("alice", hash_password("secret")) is None

    token_cache.set.assert_not_called()


def test_logout_clears_persisted_and_cached_token(service, user_dao):
    user_dao.get_by_id.return_value = make_user()
    user_dao.update_user.return_value = True

    with patch.object(user_service_module, "app_token_cache") as token_cache:
        assert service.logout(7)

    user_dao.update_user.assert_called_once_with(7, {"access_token": None})
    token_cache.delete.assert_called_once_with("old-token")


def test_logout_returns_false_for_unknown_user(service, user_dao):
    user_dao.get_by_id.return_value = None

    assert service.logout(7) is False
    user_dao.update_user.assert_not_called()


def test_list_users_and_update_user_delegate_to_dao(service, user_dao):
    params = {"role": "USER", "limit": 10}
    updates = {"email": "new@example.org"}
    expected_users = [make_user()]
    user_dao.list_users.return_value = expected_users
    user_dao.update_user.return_value = True

    assert service.list_users(params) is expected_users
    assert service.update_user(7, updates)
    user_dao.list_users.assert_called_once_with(params)
    user_dao.update_user.assert_called_once_with(7, updates)