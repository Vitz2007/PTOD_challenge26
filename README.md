# Low-burden Mode Accessibility

An entry for the PTOD (Open Data Challenge for Public Transportation in Tokyo)
2026 challenge. The app helps people who need, or prefer, a low-effort route
through Tokyo's train stations: wheelchair users, people with strollers or
luggage, older travellers, and anyone who wants to avoid crowds.

## Goals

1. **Station facility info:** show where a station's elevators, escalators,
   slopes and step-free paths are.
2. **Real-time congestion:** highlight the busy areas of a station right now,
   and point users to quieter, open spaces in the station.

## Datasets

All data comes from the ODPT challenge API (`https://api-challenge.odpt.org/api/v4`).
Checked with our key on 2026-11-03:

| Need                   | ODPT data type          | Available?                                   |
| ---------------------- | ----------------------- | -------------------------------------------- |
| Station-level detail   | `odpt:Station`          | Yes, for all major operators                 |
| Congestion (baseline)  | `odpt:PassengerSurvey`  | 8 operators, 1,184 stations (see below)      |
| Congestion (live)      | `odpt:Train`, `odpt:TrainInformation` | Yes (delays and line status, Japanese text) |
| Accessibility          | `odpt:StationFacility`  | **No**: returns 404; the dump file is not published yet |

Passenger counts exist for **JR East, Tobu, Tokyu, Seibu, Keikyu, Keio, Odakyu
and Sotetsu**. Tokyo Metro, Toei and the smaller lines have none, so they are not
supported yet. JR East counts people getting on only; the others count on and
off, so JR East figures are doubled when ranking stations against each other.

Congestion is a level for the whole station (busy / normal / quiet). Station
facilities return `null` until ODPT publishes the data. Crowding inside a station
and open space have no source in the API.

Live data varies by operator: train delays exist for JR East, Tobu, Keikyu and
Keio; line status exists for all but Odakyu and Sotetsu.

## Tech stack

| Layer    | Choice                                     |
| -------- | ------------------------------------------ |
| Backend  | Python with FastAPI, calling the ODPT API  |
| Frontend | React, as a website first                  |
| Later    | iOS app                                    |
| Editor   | VS Code                                    |

### Libraries

**Backend (Python):** in `requirements.txt`

- `fastapi`: web framework for the API
- `uvicorn`: server that runs the app
- `httpx`: async HTTP client for calling ODPT
- `pydantic-settings`: typed settings from environment variables and `.env`
- `pytest` (dev only, in `requirements-dev.txt`): tests

**Frontend (React):** in `frontend/package.json`

- `react` and `react-dom`
- `vite` (v6, pinned so it runs on Node 22.9): dev server and build
- `oxlint`: linter (needs Node 20.19+ or 22.12+)

No styling, routing or UI library yet; the frontend team will choose these.

## Roadmap

- [x] FastAPI backend split into config, ODPT client, cache, services and routes
- [x] Station congestion endpoint (yearly busy level plus live delays and status)
- [x] Tests for congestion logic and API endpoints
- [x] 8 operators supported, ranked against each other
- [x] Starter React website (operator and station search, station details)
- [ ] Station facilities, once ODPT publishes `odpt:StationFacility`
- [ ] Tokyo Metro and Toei congestion, if ODPT adds their passenger counts
- [ ] Styling and design for the website
- [ ] Station view: list of elevators, escalators, slopes and step-free paths
- [ ] Congestion view: highlight crowded areas and suggest open spaces
- [ ] Port to an iOS app

## Getting started

### Requirements

- Python 3.10+
- Node 20.19+ or 22.12+ (22.9 works, except the linter)
- An ODPT Challenge consumer key
- VS Code (recommended), with the Python extension

### Backend setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # then put your key in .env
```

### Running the backend

```bash
python main.py                                   # development, auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000  # production
```

API docs: <http://127.0.0.1:8000/api/docs>

### Running the tests

```bash
pytest
```

The tests use a fake ODPT client, so they need no network or key.

### Configuration

Settings are read from environment variables or `.env` (see `.env.example`):

| Variable               | Default                                  | Purpose                              |
| ---------------------- | ---------------------------------------- | ------------------------------------ |
| `ODPT_CONSUMER_KEY`    | required                                 | ODPT API key                         |
| `ODPT_BASE_URL`        | `https://api-challenge.odpt.org/api/v4`  | ODPT API address                     |
| `LIVE_CACHE_SECONDS`   | `30`                                     | Reuse live train data for this long  |
| `STATIC_CACHE_SECONDS` | `86400`                                  | Reuse station lists and surveys      |
| `CORS_ORIGINS`         | `["http://localhost:5173"]`              | Frontend addresses allowed to call the API |

### Frontend setup

```bash
cd frontend
npm install
npm run dev     # http://localhost:5173, /api is sent to the backend
```

To serve the website from the backend at <http://127.0.0.1:8000>, run
`npm run build` in `frontend/` and restart the backend. More detail for the
frontend team is in [`frontend/README.md`](frontend/README.md).

## API endpoints

| Method | Path                      | Description                                               |
| ------ | ------------------------- | --------------------------------------------------------- |
| GET    | `/api/health`             | Liveness check                                            |
| GET    | `/api/v1/operators`       | Supported operators                                       |
| GET    | `/api/v1/stations`        | Stations for an operator (`?operator=Keio`, JR East default) |
| GET    | `/api/v1/stations/{operator}/{name}` | Congestion and live line status for one station |
| GET    | `/api/v1/service-status`  | Live status for every line ODPT reports                   |

```bash
curl http://127.0.0.1:8000/api/v1/stations/Keio/Shinjuku
```

ODPT failures return `502` with a short message. The API key never appears in
errors or logs.

## Project structure

```
.
├── main.py                  # Dev entrypoint (python main.py)
├── app/
│   ├── main.py              # create_app(): routers, CORS, errors, frontend
│   ├── config.py            # Settings from env / .env
│   ├── cache.py             # In-memory TTL cache (swap for Redis to scale out)
│   ├── schemas.py           # Response models
│   ├── odpt/
│   │   ├── client.py        # ODPT API client
│   │   └── vocab.py         # ODPT identifiers
│   ├── services/
│   │   ├── congestion.py    # Busy-level logic (pure functions)
│   │   └── stations.py      # Combines ODPT data per station
│   └── api/
│       ├── deps.py          # Dependency injection
│       └── routes/          # health.py, stations.py
├── frontend/                # React website (see frontend/README.md)
│   └── src/
│       ├── App.jsx          # The page
│       ├── api/             # Backend calls (client.js) and useApi hook
│       └── components/      # StationSearch, StationDetail, LineStatusList
├── tests/                   # pytest suite
├── requirements.txt         # Runtime dependencies
├── requirements-dev.txt     # + test tools
└── .env.example             # Settings template
```

### Adding a feature

1. Add the ODPT data type to `app/odpt/vocab.py`.
2. Put the logic in a service under `app/services/`, using `ODPTClient` and the cache.
3. Add response models to `app/schemas.py`.
4. Add a route under `app/api/routes/` and register it in `app/main.py`.
5. Add tests under `tests/`.
