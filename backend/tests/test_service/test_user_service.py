from unittest.mock import MagicMock

from business_object.user import User
from dao.user_dao import UserDao
from service.user_service import UserService

user_list = [
  User(),
  User(),
  User()
]


# Tests de singup()

def test_signup_ok():
    """L'inscription d'un nouvel utilisateur est réussie"""

    # GIVEN
    username, email, password = "ausername", "anemail@email.fr", "acoolpassword"
    UserDao().create_user(User(username=username, email=email, password=password)) = MagicMock(
        return_value=True
    )

    # WHEN
    signed_up = UserService(
        {
            "username": username,
            "email": email,
            "password": password
        }
    )

    # THEN
    assert signed_up


def test_signup_fail():
    """L'inscription d'u nouvel utilisateur échoue car un des éléments
    n'a pas le bon format"""

    # GIVEN
    username, email, password = "ausername", 1312, "acoolpassword"
    UserDao().create_user(User(username=username, email=email, password=password)) = MagicMock(
        return_value=False
    )

    # WHEN
    signed_up = UserService(
        {
            "username": username,
            "email": email,
            "password": password
        }
    )

    # THEN
    assert not signed_up


# Tests de login()

def test_login_ok():
    """L'identification est réussie"""

    # GIVEN
    username, password_hashed = "", ""
    UserDao().get_by_username(username) = MagicMock(
        return_value=User()
    )

    # WHEN
    token = UserService().login(username, password_hashed)

    # THEN
    assert isinstance(token, str)


def test_login_wrong_info():
    """L'identification échoue car le système ne reconnaît pas les informations fournies"""

    # GIVEN
    username, password_hashed = "", ""
    UserDao().get_by_username(username) = MagicMock(
        return_value=None
    )

    # WHEN
    token = UserService().login(username, password_hashed)

    # THEN
    assert token is None


# Tests de logout()

def test_logout_ok():
    """La déconnexion est réussie"""

    # GIVEN
    id = 1
    UserDao().get_by_id(id) = MagicMock(return_value=User())

    # WHEN
    logged_out = UserService().logout(id)

    # THEN
    assert logged_out


def test_logout_wrong_id():
    """La déconnexion échoue car l'identifiant donné n'est pas reconnu"""

    # GIVEN
    id = 6566898089
    UserDao().get_by_id(id) = MagicMock(return_value=None)

    # WHEN
    logged_out = UserService().logout(id)

    # THEN
    assert not logged_out


# Tests de list_users()

def test_list_users_no_params():
    """Nous obtenons la liste des utilisateurs sans paramètres de tri"""


def test_list_users_with_params():
    """Nous obtenons la liste des utilisateurs avec un paramètre de tri"""


def test_list_users_wrong_param():
    """Nous n'obtenons pas de liste d'utilisateurs car un des paramètres rensignés n'est pas
    dans le bon format"""


# Tests de update_user()

def test_update_user_ok():
    """La mise à jour d'un utilisateur est réussie"""


def test_update_user_wrong_id():
    """Impossibilité de mettre à jour l'utilisateur car l'identifiant donné n'est pas
    reconnu"""


def test_update_user_wrong_param():
    """Impossibilité de mettre à jour l'utilisateur car l'un des paramètres donné n'est
    pas dans le bon format"""
