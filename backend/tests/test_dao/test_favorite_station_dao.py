import pytest
from _pytest.fixtures import FixtureRequest

from business_object.station_information import StationInformation
from dao.favorite_station_dao import FavoriteStationDAO
from dao.station_dao import StationDAO
from utils.db_connection import DbConnection
from utils.settings import get_settings

TEST_STATION_ID = "favorite-dao-test-station"
TEST_USERNAME = "favorite-dao-test-user"
TEST_EMAIL = "favorite-dao-test@example.test"


@pytest.fixture
def favorite_dao_context(request: FixtureRequest):
    settings = get_settings().model_copy(update={"postgres_schema": "veloscope_test"})
    db_connection = DbConnection(settings)
    station_dao = StationDAO(db_connection)
    favorite_dao = FavoriteStationDAO(db_connection)

    def remove_test_data():
        with db_connection.get_connection() as connection:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'DELETE FROM "user" WHERE username = %(username)s',
                        {"username": TEST_USERNAME},
                    )
                    cursor.execute(
                        """
                        DELETE FROM station_information
                        WHERE station_id = %(station_id)s
                        """,
                        {"station_id": TEST_STATION_ID},
                    )

    def cleanup():
        try:
            remove_test_data()
        finally:
            db_connection.close()

    request.addfinalizer(cleanup)
    remove_test_data()

    station = StationInformation(
        station_id=TEST_STATION_ID,
        name="Favorite DAO integration test",
        short_name=None,
        lat=48.8566,
        lon=2.3522,
        address="",
        is_virtual_station=False,
        station_area=None,
        contact_phone=None,
        capacity=10,
        is_charging_station=False,
    )
    assert station_dao.upsert_station_info(station)
    saved_station = station_dao.get_by_id(TEST_STATION_ID)
    assert saved_station is not None
    assert saved_station.station_id == TEST_STATION_ID

    with db_connection.get_connection() as connection:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO "user" (username, password_hashed, email, role)
                    VALUES (%(username)s, 'test-hash', %(email)s, 'USER')
                    RETURNING user_id
                    """,
                    {"username": TEST_USERNAME, "email": TEST_EMAIL},
                )
                user_id = cursor.fetchone()["user_id"]

    return favorite_dao, station_dao, user_id, TEST_STATION_ID


def test_add_favorite_and_reject_duplicate(favorite_dao_context):
    favorite_dao, _, user_id, station_id = favorite_dao_context

    assert favorite_dao.add_favorite(user_id, station_id)
    assert not favorite_dao.add_favorite(user_id, station_id)


def test_add_favorite_for_unknown_user(favorite_dao_context):
    favorite_dao, _, user_id, station_id = favorite_dao_context

    assert not favorite_dao.add_favorite(user_id + 10_000_000, station_id)


def test_add_favorite_for_unknown_station(favorite_dao_context):
    favorite_dao, _, user_id, _ = favorite_dao_context

    assert not favorite_dao.add_favorite(user_id, "unknown-station")


def test_list_favorites_from_database(favorite_dao_context):
    favorite_dao, station_dao, user_id, station_id = favorite_dao_context
    station = station_dao.get_by_id(station_id)
    assert station is not None
    assert favorite_dao.add_favorite(user_id, station_id)

    favorites = favorite_dao.list_favorites({"user_id": user_id})

    assert len(favorites) == 1
    assert favorites[0].station_id == station.station_id
    assert favorites[0].name == station.name


def test_list_favorites_for_unknown_user(favorite_dao_context):
    favorite_dao, _, user_id, _ = favorite_dao_context

    assert favorite_dao.list_favorites({"user_id": user_id + 10_000_000}) is None


def test_count_favorites_from_database(favorite_dao_context):
    favorite_dao, _, user_id, station_id = favorite_dao_context
    assert favorite_dao.add_favorite(user_id, station_id)

    assert favorite_dao.count_favorites([station_id]) == {station_id: 1}


def test_count_favorites_for_unknown_station(favorite_dao_context):
    favorite_dao, _, _, _ = favorite_dao_context

    assert favorite_dao.count_favorites(["unknown-station"]) is None


def test_count_favorites_for_empty_input(favorite_dao_context):
    favorite_dao, _, _, _ = favorite_dao_context

    assert favorite_dao.count_favorites([]) == {}


def test_remove_favorite(favorite_dao_context):
    favorite_dao, _, user_id, station_id = favorite_dao_context
    assert favorite_dao.add_favorite(user_id, station_id)

    assert favorite_dao.remove_favorite(user_id, station_id)
    assert not favorite_dao.remove_favorite(user_id, station_id)
