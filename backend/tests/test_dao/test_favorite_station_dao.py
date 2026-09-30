import os
from unittest.mock import patch

import psycopg2
import pytest
from utils.reset_database import ResetDatabase

from business_object.user import User
from dao.user_dao import UserDao


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation de la base de données pour les tests"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


# Tests de add_favorite()

def test_add_favorite_possible():
  """Réussite de l'ajout de la station à la liste des favoris"""


def test_add_favorite_already_favorite():
  """La station est déjà présente dans la liste des favoris"""

def test_add_favorite_non_existing():
  """Impossibilité d'ajouter la station à la liste des favoris car son identifiant
  n'est pas reconnu"""

