#

## Setup database

**Step 1:** Launch a PostgreSQL (e.g. a PostgreSQL service on Datalabs)

**Step 2:** Run `data/init_db.sql` to create the database and tables (e.g. using a CloudBeaver service on Datalabs)

## Inside `backend` folder

`cd backend` to go into backend/ from project root

**Step 1:** Create `.env` file in the `backend` folder with these variables:

```
postgres_host=fill_your_own
postgres_port=fill_your_own
postgres_database=fill_your_own
postgres_user=fill_your_own
postgres_password=fill_your_own
postgres_schema=veloscope

system_information_feed_url=https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ae/fr/system_information.json
station_information_feed_url=https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ae/fr/station_information.json
station_status_feed_url=https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ae/fr/station_status.json
```

**Step 2:** Install the required packages:

`uv sync` to get production's required packages

`uv sync --all-extras` to get development's required packages

**Step 3:** Start the webservice:

`uv run ./src/main.py`

**Optional:** Run mypy for type checking:

`uv run mypy src`
