#

`cd backend` to go into backend/ from project root

## Inside `backend` folder

`uv sync` to get production's required packages

`uv sync --all-extras` to get development's required packages

`uv run mypy src` for mypy check

`uv run ./src/main.py` to start your webservice (with configuration in `backend/env`)
