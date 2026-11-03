import { getStation } from '../api/client'
import { useApi } from '../api/useApi'
import LineStatusList from './LineStatusList'

// Congestion, live status and facilities for one station.
export default function StationDetail({ operator, name }) {
  const { data: station, error, loading } = useApi(() => getStation(operator, name), [operator, name])

  if (loading) return <p>Loading {name}…</p>
  if (error) return <p role="alert">{error.message}</p>
  if (!station) return null

  const { congestion } = station

  return (
    <section>
      <h2>
        {station.name.en} ({station.name.ja}), {station.operator.name}
      </h2>

      <h3>Congestion</h3>
      <ul>
        <li>Busy level: {congestion.busy_level}</li>
        <li>
          Passengers per day: {congestion.passengers_per_day.toLocaleString()}{' '}
          ({congestion.includes_alighting ? 'getting on and off' : 'getting on'}, {congestion.survey_year} survey)
        </li>
        <li>
          Live delay: {congestion.live_delay_minutes == null ? 'no data' : `${congestion.live_delay_minutes} min`}
        </li>
      </ul>

      <h3>Line status</h3>
      <LineStatusList lines={station.service_status} />

      <h3>Facilities</h3>
      {station.facilities ? (
        <ul>
          {station.facilities.map((f, i) => (
            <li key={i}>
              {f.kind}
              {f.description && `: ${f.description}`}
            </li>
          ))}
        </ul>
      ) : (
        <p>Not available yet.</p>
      )}

      {station.notes.map((note) => (
        <p key={note}>
          <small>{note}</small>
        </p>
      ))}
    </section>
  )
}
