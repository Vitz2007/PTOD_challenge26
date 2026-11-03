// All calls to the backend live here, so components never build URLs themselves.
// Endpoint docs: http://127.0.0.1:8000/api/docs

const BASE = '/api/v1'

async function get(path) {
  const response = await fetch(BASE + path)
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed (${response.status})`)
  }
  return response.json()
}

// [{ code, name }], e.g. { code: 'Keio', name: 'Keio' }
export const getOperators = () => get('/operators')

// [{ id, name: { en, ja }, railway }]
export const getStations = (operator) => get(`/stations?operator=${encodeURIComponent(operator)}`)

// { id, operator: { code, name }, name, railways,
//   congestion: { passengers_per_day, includes_alighting, survey_year, busy_level, live_delay_minutes },
//   service_status: [{ railway, status, text }], facilities, notes }
export const getStation = (operator, name) =>
  get(`/stations/${encodeURIComponent(operator)}/${encodeURIComponent(name)}`)

// [{ railway, status, text }]
export const getServiceStatus = () => get('/service-status')
