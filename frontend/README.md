# Véloscope - Frontend Web Application

Interactive web application for the **Véloscope** bike-sharing analytics and recommendation platform, built with **Streamlit**, **Pandas**, and **Folium**.

---

## Features

- **Interactive Station Map & List**: Filter stations in real-time, with paginated tabular view and interactive map.
- **Smart Proximity Recommendation**: Locate the nearest station based on any address, filtering by bike type or dock availability via Haversine distance calculations.
- **Station Deep-Dive Analytics**: View live availability, historical trends (1 hour, 24 hours, daily), and calculated reliability scores (0–100).
- **User Authentication & Favorites**: Register, log in, and manage personal favorite stations with seamless session persistence.

---

## Project Structure

```text
frontend/
├── src/
│   ├── pages/
│   │   ├── connexion.py            # User authentication / Login page
│   │   ├── favorite_stations.py    # Saved user favorites page
│   │   ├── home.py                 # Landing page & platform overview
│   │   ├── inscription.py          # User registration / Signup page
│   │   ├── list_stations.py        # Station explorer with search & map
│   │   ├── station_info.py         # Detailed analytics & historical charts
│   │   └── velo_a_proximite.py     # Smart proximity recommendation tool
│   ├── utils/
│   │   ├── api_client.py           # REST API client connecting to backend
│   │   ├── env_variables.py        # Environment variables loader
│   │   └── log_init.py             # Streamlit session logging initializer
│   └── app.py                      # Application entrypoint & navigation router
├── .env.example                    # Template for frontend environment variables
├── pyproject.toml                  # Dependencies & tool configurations
└── README.md
```

---

## Prerequisites

- **Python 3.13+**
- **uv** package manager: [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- Running **Véloscope Backend** (see `backend/README.md`)

---

## Configuration

Navigate to the `frontend/` directory and configure the environment variables:

```bash
cd frontend
cp .env.example .env
```

The default `.env` points to the local backend on port `5000`:

```ini
BACKEND_URL=http://localhost:5000
BACKEND_TIMEOUT=10
```

---

## Installation

Using `uv`:

```bash
# Install all required dependencies
uv sync

# Or with dev dependencies (linters, formatters)
uv sync --all-extras
```

---

## Running the Application

Make sure the backend API is already running (see [backend/README.md](../backend/README.md)), then start the Streamlit frontend:

```bash
uv run streamlit run src/app.py
```

The web interface will automatically open in your browser at:
👉 **[http://localhost:8501](http://localhost:8501)**

---

## Code Quality & Formatting

Lint and format frontend code using **Ruff**:

```bash
# Check code style
uv run ruff check .

# Automatically apply safe fixes
uv run ruff check --fix .

# Format code
uv run ruff format .
```
