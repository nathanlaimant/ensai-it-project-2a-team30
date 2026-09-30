from unittest.mock import MagicMock

from business_object.user import User
from dao.user_dao import UserDao
from service.user_service import UserService

user_list = [
  User(),
  User(),
  User(),
]


# Tests de singup()

def test_signup_ok():
  """L'inscription d'un nouvel utilisateur est réussie"""
