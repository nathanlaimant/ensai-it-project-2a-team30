# Véloscope - Backend API

Backend REST API for the **Véloscope** platform, built with **FastAPI**, **PostgreSQL**, and background **APScheduler** jobs to collect, process, and serve real-time and historical bike-sharing GBFS feeds.

---

## Table of Contents

- [Véloscope - Backend API](#véloscope---backend-api)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Project Structure](#project-structure)
  - [Database Setup](#database-setup)
  - [Environment Configuration](#environment-configuration)
    - [1. Runtime Environment (`.env`)](#1-runtime-environment-env)
    - [2. Test Environment (`.test_env`)](#2-test-environment-test_env)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
    - [Verification \& Documentation](#verification--documentation)
  - [Running Tests](#running-tests)
  - [Test Coverage](#test-coverage)
    - [1. Default Run (Terminal Report with Missing Lines)](#1-default-run-terminal-report-with-missing-lines)
    - [2. Generate Interactive HTML Report](#2-generate-interactive-html-report)
    - [3. Alternative: Using `coverage` CLI Directly](#3-alternative-using-coverage-cli-directly)
  - [Code Quality \& Linting](#code-quality--linting)
    - [Type Checking (Mypy)](#type-checking-mypy)
    - [Linting (Ruff)](#linting-ruff)
    - [Code Formatting (Ruff)](#code-formatting-ruff)

---

## Prerequisites

- **Python 3.13+**
- **uv** (package and environment manager): [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **PostgreSQL** instance (local, Datalabs, Aiven Cloud, Supabase, etc.)

---

## Project Structure

```text
backend/
├── src/
│   ├── business_object/    # Domain entities & data models (User, StationInformation, StationStatus, etc.)
│   ├── controller/         # FastAPI route controllers / handlers
│   ├── dao/                # Data Access Objects (SQL queries & PostgreSQL interactions)
│   ├── dependencies/       # Dependency injection providers (DB pool, HTTP client, scheduler)
│   ├── service/            # Core business logic, recommendation algorithms & aggregators
│   ├── utils/              # Database connection pooler, settings, and logging helpers
│   └── main.py             # Application entrypoint & FastAPI app definition
├── tests/
│   ├── test_dao/           # Unit & integration tests for Data Access Objects
│   └── test_service/       # Unit tests for business services
├── .env                    # Runtime environment variables (ignored by git)
├── .test_env               # Test environment variables (pointing to test schema)
├── pyproject.toml          # Project configuration, dependencies, and test/coverage settings
└── README.md
```

---

## Database Setup

Initialize the required schemas and tables using the SQL scripts located in the root `data/` directory:

1. **Production / Runtime Schema (`veloscope`)**:
   Execute `data/init_db.sql` on your PostgreSQL database (e.g., using CloudBeaver, DBeaver, or `psql`).
   *(Optional)* Execute `data/pop_db.sql` to populate initial seed data.

2. **Test Schema (`veloscope_test`)**:
   Execute `data/init_db_test.sql` to create the isolated schema used by the test suite.
   *(Optional)* Execute `data/pop_db_test.sql` for test seed data.

---

## Environment Configuration

Navigate to the `backend/` directory from the repository root:

```bash
cd backend
```

### 1. Runtime Environment (`.env`)

Copy the provided template and fill in your PostgreSQL database credentials:

```bash
cp .env.example .env
```

The runtime `.env` contains:

```ini
postgres_host=your_postgres_host
postgres_port=your_postgres_port
postgres_database=your_database_name
postgres_user=your_username
postgres_password=your_password
postgres_schema=veloscope

# Server Port (defaults to 5000)
uvicorn_port=5000

# GBFS feed endpoints (e.g., Vélhop Strasbourg v2.3)
system_information_feed_url=https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ae/fr/system_information.json
station_information_feed_url=https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ae/fr/station_information.json
station_status_feed_url=https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ae/fr/station_status.json
```

### 2. Test Environment (`.test_env`)

Tests run in isolation on the `veloscope_test` schema. Copy the test environment template:

```bash
cp .test_env.example .test_env
```

The test `.test_env` targets the dedicated test schema:

```ini
postgres_host=your_postgres_host
postgres_port=your_postgres_port
postgres_database=your_database_name
postgres_user=your_username
postgres_password=your_password
postgres_schema=veloscope_test

system_information_feed_url=http://mock
station_information_feed_url=http://mock
station_status_feed_url=http://mock
```

---

## Installation

Using `uv`:

```bash
# Install production dependencies only
uv sync

# Install all dependencies including development & testing tools (pytest, coverage, ruff, mypy)
uv sync --all-extras
```

---

## Running the Application

Start the backend service:

```bash
uv run src/main.py
```

### Verification & Documentation

- **Health / DB Connectivity check**: [http://localhost:5000/db](http://localhost:5000/db)
- **Interactive API Documentation (Swagger UI)**: [http://localhost:5000/docs](http://localhost:5000/docs)
- **Alternative Documentation (ReDoc)**: [http://localhost:5000/redoc](http://localhost:5000/redoc)

---

## Running Tests

All tests read configuration from `.test_env` and run in complete isolation against the `veloscope_test` schema.

> **Note on Test Environment Setup**:
> Before running tests, ensure you have initialized the test schema by running `data/init_db_test.sql` (and optionally `data/pop_db_test.sql`) in PostgreSQL, and created `backend/.test_env` (e.g. `cp .test_env.example .test_env`).

```bash
# Run all tests
uv run pytest

# Run only service & aggregation tests
uv run pytest tests/test_service

# Run only DAO tests
uv run pytest tests/test_dao

# Run a specific test suite
uv run pytest tests/test_dao/test_station_dao.py
uv run pytest tests/test_dao/test_user_dao.py
uv run pytest tests/test_dao/test_favorite_station_dao.py
uv run pytest tests/test_dao/test_station_status_dao.py
uv run pytest tests/test_dao/test_station_status_hourly_dao.py

# Run a specific test case by name
uv run pytest tests/test_dao/test_station_dao.py -k test_get_by_id_ok

# Run tests without stopping at first failure (override -x)
uv run pytest -v -o addopts="" tests/test_dao
```

---

## Test Coverage

Coverage settings are defined in `pyproject.toml` under `[tool.coverage.run]` (restricting checks exclusively to `service/` and `dao/`) and enabled by default in `addopts`.

### 1. Default Run (Terminal Report with Missing Lines)

Coverage on `service/` and `dao/` runs automatically with pytest:

```bash
uv run pytest tests/test_dao
```

### 2. Generate Interactive HTML Report

To generate an interactive HTML coverage report alongside the test run:

```bash
uv run pytest --cov-report=html tests/test_dao
```

The report is saved in `coverage_report/`. Open `coverage_report/index.html` in your browser.

### 3. Alternative: Using `coverage` CLI Directly

Because `source = ["src/service", "src/dao"]` is configured in `pyproject.toml`, the standard `coverage` tool automatically restricts checks to these packages:

```bash
# Run tests under coverage measurement
uv run coverage run -m pytest tests/test_dao

# View report with missing lines
uv run coverage report -m

# Generate HTML report
uv run coverage html
```

---

## Code Quality & Linting

### Type Checking (Mypy)

```bash
uv run mypy src
```

### Linting (Ruff)

```bash
# Check code style and common bugs
uv run ruff check src tests

# Automatically fix fixable lint errors
uv run ruff check --fix src tests
```

### Code Formatting (Ruff)

```bash
# Check formatting
uv run ruff format --check src tests

# Auto-format all Python files
uv run ruff format src tests
```
