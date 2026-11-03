import React from 'react';
import { useStation } from './hooks/useStationData';

// Details for the station clicked on the map
export default function StationDetail({ operator, name }) {
  const { data: station, isLoading, error } = useStation(operator, name);

  if (isLoading) return <p>Loading {name}...</p>;
  if (error) return <p>Could not load {name}.</p>;
  if (!station) return null;

  const { congestion } = station;

  return (
    <section>
      <h2>{station.name.en} ({station.name.ja})</h2>
      <p>{station.operator.name}</p>

      <h3>Congestion</h3>
      <ul>
        <li>Busy level: {congestion.busy_level}</li>
        <li>Passengers per day: {congestion.passengers_per_day.toLocaleString()} ({congestion.survey_year} survey)</li>
        <li>Live delay: {congestion.live_delay_minutes ?? 'no data'} min</li>
      </ul>

      <h3>Line status</h3>
      <ul>
        {station.service_status.map((line) => (
          <li key={line.railway}>{line.railway.split('.').pop()}: {line.text || line.status}</li>
        ))}
      </ul>

      <h3>Facilities</h3>
      <p>{station.facilities ? station.facilities.length + ' facilities' : 'Not available yet.'}</p>
    </section>
  );
}
