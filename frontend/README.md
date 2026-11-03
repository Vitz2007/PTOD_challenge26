# Frontend

Starter React app for Low-burden Mode Accessibility. It is deliberately plain
(no styling, no UI library), so the frontend team can choose their own.

## Run it

You need Node 20.19+ or 22.12+ for the linter. The app itself also builds on
Node 22.9 (Vite 6 is pinned for that reason).

```bash
# 1. Start the backend from the project root
python main.py

# 2. Start the frontend
cd frontend
npm install
npm run dev        # http://localhost:5173, /api is proxied to the backend
```

To serve it from the backend at <http://127.0.0.1:8000>, run `npm run build`
and restart the backend.

## Structure

```
src/
├── main.jsx                   # Mounts <App />
├── App.jsx                    # The page: search box, then station details
├── api/
│   ├── client.js              # Every backend call (getStations, getStation, getServiceStatus)
│   └── useApi.js              # Hook: { data, error, loading } for any API call
└── components/
    ├── StationSearch.jsx      # Station name input with suggestions
    ├── StationDetail.jsx      # Congestion, line status, facilities for one station
    └── LineStatusList.jsx     # List of lines and their live status
```

## Working on it

- **New data:** add a function to `api/client.js`, then use it in a component
  with `useApi`. Don't call `fetch` directly from components.
- **Response shapes:** see the comments in `api/client.js`, or try the endpoints
  at <http://127.0.0.1:8000/api/docs>.
- **Styling and routing:** none yet; add whichever library the team picks.

## Data limits

- Congestion covers 8 operators (JR East, Tobu, Tokyu, Seibu, Keikyu, Keio, Odakyu, Sotetsu), as one level per station. Tokyo Metro and Toei have no passenger counts in the challenge API.
- `facilities` is always `null` for now, because ODPT hasn't published it.
- Line status text is Japanese only.
