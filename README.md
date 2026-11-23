# Véloscope - Bike-Sharing Platform

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://www.postgresql.org/)

**ENSAI 2nd Year Computer Science Project - Team 30**  
**Team Members:**  

- **Antonin PRADEL**  
- **Martin DUBOS-DANIELLI**  
- **Minh Quang KIEU**  
- **Nathan LAIMANT**  
- **Victor NEMBRINI**  

---

## Overview

**Véloscope** is an end-to-end bike-sharing monitoring, analytics, and recommendation platform tailored for networks using the GBFS (General Bikeshare Feed Specification) standard.

The platform continuously ingests real-time bike and dock availability, performs automated hourly aggregations to evaluate station reliability, exposes a secure REST API, and provides an intuitive web interface for end users.

### Key Features

1. **Live GBFS Feed Ingestion**: Autonomous ingestion of `station_information`, `station_status` and `system_information` feeds powered by an asynchronous background scheduler (**APScheduler**).
2. **Station Reliability Score & Analytics**: Automated hourly bucket calculation assessing station empty/full events, and computing a reliability score ($0$ to $100$).
3. **Smart Proximity Recommendation**: Locate the closest optimal station based on any address using Haversine distance, with custom filters.
4. **Interactive Web Dashboard**: Streamlit frontend featuring interactive maps, real-time availability filters, and historical trend charts.
5. **User Accounts & Favorites**: Secure user authentication (bcrypt password hashing, Bearer tokens) allowing users to save and track favorite stations.

---

## Architecture

The project strictly follows layered architecture principles:

```text
ensai-it-project-2a-team30/
├── backend/                  # REST API & background services
│   ├── src/
│   │   ├── business_object/  # Domain entities (User, StationStatus, etc.)
│   │   ├── controller/       # FastAPI endpoints & routers
│   │   ├── dao/              # PostgreSQL Data Access Objects
│   │   ├── dependencies/     # Dependency injection (DB, HTTP, Scheduler)
│   │   ├── schema/           # Pydantic request & response models
│   │   ├── service/          # Business logic, aggregations, recommendation
│   │   └── utils/            # DB connection pool, configuration & logging
│   ├── tests/                # Unit and integration tests (pytest)
│   └── README.md             # Developer documentation
├── frontend/                 # Interactive Streamlit application
│   ├── src/
│   │   ├── pages/            # Multi-page views (Search, Favorites, etc.)
│   │   └── utils/            # API client & session helpers
│   └── README.md             # Frontend guide
├── data/                     # Database creation & seed scripts
│   ├── init_db.sql           # Schema definition (veloscope)
│   ├── init_db_test.sql      # Isolated test schema (veloscope_test)
│   ├── star_rennes/          # LE vélo STAR (Rennes) dataset
│   │   ├── pop_db.sql
│   │   ├── pop_db_station_status.sql
│   │   └── pop_db_station_status_hourly.sql
│   └── velhop_strasbourg/    # Vélhop (Strasbourg) dataset
│       ├── pop_db.sql
│       ├── pop_db_station_status.sql
│       └── pop_db_station_status_hourly.sql
└── README.md                 # User guide (this document)
```

---

## Quick Start Guide

Follow these steps to set up and run the entire application on your machine.

### Prerequisites

- **Python 3.13+**
- **uv** (recommended package and project manager): [Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)
- Access to a **PostgreSQL** instance

---

### Step 1: Database Initialization

Connect to your PostgreSQL database and execute the initialization scripts located in `data/`:

1. **Create tables**: Execute [`data/init_db.sql`](data/init_db.sql) (creates the `veloscope` schema and all required tables).
2. **Populate initial data (choose one GBFS system)**:
   Execute the scripts inside either [`data/star_rennes/`](data/star_rennes/) or [`data/velhop_strasbourg/`](data/velhop_strasbourg/) in the following order:
   - `pop_db.sql`: inserts demo accounts (`admin` / `user0`, password `1`), `system_information`, and `station_information`.
   - *(Optional)* `pop_db_station_status.sql`: inserts ~48 hours of raw 5-minute station status snapshots.
   - *(Optional)* `pop_db_station_status_hourly.sql`: inserts 121 hours (~5 days) of pre-computed hourly aggregates and reliability scores.

#### Available Datasets

| Dataset | System ID | Stations | Raw Status Rows | Hourly Rows | Notes |
|---|---|---|---|---|---|
| **LE vélo STAR (Rennes)** ([`data/star_rennes/`](data/star_rennes/)) | `le_velo_star` | 57 | 32,889 | 6,897 | Includes `address` (`short_name` is `NULL`); `FUNCTIONAL`, `EMPTY`, and `FULL` states; mechanical bikes only (`electric = 0`) |
| **Vélhop (Strasbourg)** ([`data/velhop_strasbourg/`](data/velhop_strasbourg/)) | `nextbike_ae` | 40 | 23,040 | 4,840 | Includes `short_name` (`address` is `NULL`); `FUNCTIONAL` and `EMPTY` states; mechanical bikes only (`electric = 0`) |

> **Note**: Both datasets cover `2026-11-18 21:00` to `2026-11-23 22:39 UTC`. Make sure the GBFS feed URLs in `backend/.env` match your chosen city when running live ingestion.

---

### Step 2: Launch the Backend API

1. Open a terminal and navigate to `backend/`:

   ```bash
   cd backend
   ```

2. Copy the environment template and adjust your PostgreSQL credentials:

   ```bash
   cp .env.example .env
   ```

   *(Ensure `postgres_host`, `postgres_port`, `postgres_user`, `postgres_password`, and `postgres_database` match your database).*

3. Install dependencies and start the backend:

   ```bash
   uv sync
   uv run src/main.py
   ```

4. Verify that the backend is running:
   - **Health Check**: [http://localhost:5000/db](http://localhost:5000/db)
   - **Interactive API Documentation (Swagger)**: [http://localhost:5000/docs](http://localhost:5000/docs)
   - **Alternative Documentation (ReDoc)**: [http://localhost:5000/redoc](http://localhost:5000/redoc)

---

### Step 3: Launch the Frontend Web Application

1. Open a **second terminal** and navigate to `frontend/`:

   ```bash
   cd frontend
   ```

2. Copy the frontend environment template:

   ```bash
   cp .env.example .env
   ```

3. Install dependencies and start Streamlit:

   ```bash
   uv sync
   uv run streamlit run src/app.py
   ```

4. Open your browser at:
   👉 **[http://localhost:8501](http://localhost:8501)**

---

## Developer & Technical Documentation

For in-depth developer information, architecture patterns, test suites, and coverage reports:

- 📖 **Backend Developer Documentation**: See [backend/README.md](backend/README.md)
  - Detailed layered architecture (DAO, Service, Controller, BO)
  - Comprehensive unit test suite
  - APScheduler cron configurations & GBFS ingestion strategies
  - Linting (`ruff`) and static type-checking (`mypy`) instructions
- 🖥️ **Frontend Documentation**: See [frontend/README.md](frontend/README.md)
