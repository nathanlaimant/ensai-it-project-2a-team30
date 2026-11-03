from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from business_object.user import User
from dao.user_dao import UserDAO
from service.user_service import UserService
from utils.security import hash_password


@pytest.fixture
def user_dao():
    return MagicMock(spec=UserDAO)


@pytest.fixture
def user_service(user_dao):
    return UserService(user_dao)


def make_user(**overrides):
    values = {
        "user_id": 1,
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


def test_signup_creates_user_with_hashed_password(user_service, user_dao):
    user_dao.create_user.return_value = True

    assert user_service.signup(
        {"username": " alice ", "email": " alice@example.org ", "password": "secret"}
    )

    created_user = user_dao.create_user.call_args.args[0]
    assert created_user.username == "alice"
    assert created_user.email == "alice@example.org"
    assert created_user.password_hashed == hash_password("secret")


def test_signup_rejects_invalid_data(user_service, user_dao):
    assert not user_service.signup(
        {"username": "alice", "email": "alice@example.org", "password": " "}
    )
    user_dao.create_user.assert_not_called()


def test_login_rejects_unknown_user(user_service, user_dao):
    user_dao.get_by_username.return_value = None

    assert user_service.login("alice", hash_password("secret")) is None


def test_logout_clears_user_token(user_service, user_dao):
    user_dao.get_by_id.return_value = make_user()
    user_dao.update_user.return_value = True

    assert user_service.logout(1)
    user_dao.update_user.assert_called_once_with(1, {"access_token": None})


def test_list_users_and_update_user_delegate_to_dao(user_service, user_dao):
    query_params = {"username": "alice", "limit": 1}
    updates = {"email": "new@example.org"}
    users = [make_user()]
    user_dao.list_users.return_value = users
    user_dao.update_user.return_value = True

    assert user_service.list_users(query_params) is users
    assert user_service.update_user(1, updates)
    user_dao.list_users.assert_called_once_with(query_params)
    user_dao.update_user.assert_called_once_with(1, updates)
