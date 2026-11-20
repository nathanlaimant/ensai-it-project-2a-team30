from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from business_object.system_information import SystemInformation
from dao.system_information_dao import SystemInformationDAO
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
def system_information_dao(db_connection):
    """Instancie le DAO avec la connexion de test."""
    return SystemInformationDAO(db_connection)


@pytest.fixture(autouse=True)
def clean_system_information(db_connection):
    """Nettoie la table system_information avant et après chaque test."""
    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM system_information WHERE system_id LIKE 'test_%';"
                )
    yield
    with db_connection.get_connection() as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM system_information WHERE system_id LIKE 'test_%';"
                )


# =========================================================================
# Tests de upsert_system_info()
# =========================================================================


def test_upsert_system_info_ok(system_information_dao):
    """Insertion réussie de toutes les informations d'un système."""
    # GIVEN
    sys_info = SystemInformation(
        system_id="test_sys_full",
        language="fr",
        name="Vélhop Strasbourg Test",
        url="https://velhop.strasbourg.eu",
        start_date=date(2020, 1, 15),
        phone_number="+33388000000",
        email="support@velhop.eu",
        timezone="Europe/Paris",
    )

    # WHEN
    result = system_information_dao.upsert_system_info(sys_info)

    # THEN
    assert result is True

    # Vérification via la méthode get_system_info du DAO
    fetched = system_information_dao.get_system_info(sys_info.system_id)
    assert fetched is not None
    assert fetched.system_id == "test_sys_full"
    assert fetched.language == "fr"
    assert fetched.name == "Vélhop Strasbourg Test"
    assert fetched.url == "https://velhop.strasbourg.eu"
    assert fetched.start_date == date(2020, 1, 15)
    assert fetched.phone_number == "+33388000000"
    assert fetched.email == "support@velhop.eu"
    assert fetched.timezone == "Europe/Paris"


def test_upsert_system_info_conflict_update(system_information_dao):
    """Mise à jour en conflit (ON CONFLICT DO UPDATE) pour un system_id déjà existant."""
    # GIVEN
    initial = SystemInformation(
        system_id="test_sys_conflict",
        language="fr",
        name="Ancien Nom",
        url="https://old.url",
        start_date=date(2018, 5, 10),
        phone_number="0102030405",
        email="old@email.com",
        timezone="Europe/Paris",
    )
    system_information_dao.upsert_system_info(initial)

    updated = SystemInformation(
        system_id="test_sys_conflict",
        language="en",
        name="Nouveau Nom",
        url="https://new.url",
        start_date=date(2022, 9, 20),
        phone_number="0908070605",
        email="new@email.com",
        timezone="America/New_York",
    )

    # WHEN
    result = system_information_dao.upsert_system_info(updated)

    # THEN
    assert result is True

    fetched = system_information_dao.get_system_info(updated.system_id)
    assert fetched is not None
    assert fetched.system_id == "test_sys_conflict"
    assert fetched.language == "en"
    assert fetched.name == "Nouveau Nom"
    assert fetched.url == "https://new.url"
    assert fetched.start_date == date(2022, 9, 20)
    assert fetched.phone_number == "0908070605"
    assert fetched.email == "new@email.com"
    assert fetched.timezone == "America/New_York"


def test_upsert_system_info_none(system_information_dao):
    """Retourne False immédiatement lorsque system_info est None."""
    # WHEN
    result = system_information_dao.upsert_system_info(None)

    # THEN
    assert result is False


def test_upsert_system_info_query_execution_exception():
    """Retourne False lorsqu'une exception survient lors de l'exécution de la requête SQL."""
    # GIVEN
    mock_db = MagicMock()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_db.get_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Erreur de syntaxe ou contrainte SQL")

    dao = SystemInformationDAO(mock_db)
    sys_info = SystemInformation(
        system_id="test_sys_sql_err",
        language="fr",
        name="Erreur SQL",
        url=None,
        start_date=None,
        phone_number=None,
        email=None,
        timezone="Europe/Paris",
    )

    # WHEN
    result = dao.upsert_system_info(sys_info)

    # THEN
    assert result is False


# =========================================================================
# Tests de get_system_info()
# =========================================================================


def test_get_system_info_by_id_ok(system_information_dao):
    """Récupération réussie d'un système par son identifiant unique."""
    # GIVEN
    sys_info = SystemInformation(
        system_id="test_sys_get_id",
        language="fr",
        name="Vélhop Test Retrieval",
        url="https://velhop.eu",
        start_date=date(2021, 3, 1),
        phone_number="0388112233",
        email="info@velhop.eu",
        timezone="Europe/Paris",
    )
    assert system_information_dao.upsert_system_info(sys_info) is True

    # WHEN
    fetched = system_information_dao.get_system_info(sys_info.system_id)

    # THEN
    assert fetched is not None
    assert fetched.system_id == "test_sys_get_id"
    assert fetched.language == "fr"
    assert fetched.name == "Vélhop Test Retrieval"
    assert fetched.url == "https://velhop.eu"
    assert fetched.start_date == date(2021, 3, 1)
    assert fetched.phone_number == "0388112233"
    assert fetched.email == "info@velhop.eu"
    assert fetched.timezone == "Europe/Paris"


def test_get_system_info_first_available(system_information_dao):
    """Récupération du premier système enregistré lorsque system_id est None."""
    # GIVEN
    sys_info = SystemInformation(
        system_id="test_sys_first",
        language="en",
        name="Default System",
        url=None,
        start_date=None,
        phone_number=None,
        email=None,
        timezone="UTC",
    )
    assert system_information_dao.upsert_system_info(sys_info) is True

    # WHEN
    fetched = system_information_dao.get_system_info()

    # THEN
    assert fetched is not None
    assert isinstance(fetched, SystemInformation)
    assert fetched.system_id is not None


def test_get_system_info_unknown_id(system_information_dao):
    """Retourne None lorsqu'aucun système ne correspond au system_id demandé."""
    # WHEN
    fetched = system_information_dao.get_system_info("test_sys_non_existent")

    # THEN
    assert fetched is None


def test_get_system_info_db_exception():
    """Retourne None lorsqu'une exception survient lors de la requête SQL."""
    # GIVEN
    mock_db = MagicMock()
    mock_db.get_connection.side_effect = Exception("Erreur base de données")
    dao = SystemInformationDAO(mock_db)

    # WHEN
    fetched = dao.get_system_info("test_sys_err")

    # THEN
    assert fetched is None
