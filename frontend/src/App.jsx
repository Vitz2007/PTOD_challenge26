import { useState } from 'react'
import StationDetail from './components/StationDetail'
import StationSearch from './components/StationSearch'
import StationMap from './StationMap'

// Sample GeoJSON data for testing related purposes showing path outside Tokyo Station
const sampleHokoNaviData = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { has_stairs: 0, name: 'Accessible Path A' },
      geometry: {
        type: 'LineString',
        coordinates: [
          [139.7671, 35.6812],
          [139.768, 35.682],
        ],
      },
    },
  ],
}

export default function App() {
  const [station, setStation] = useState(null)

  return (
    <main>
      <h1>Low-burden Mode Accessibility</h1>
      <p>Look up a station to see how busy it is and whether its lines are running normally.</p>

      <StationSearch onSelect={setStation} />

      {station && <StationDetail operator={station.operator} name={station.name} />}

      <h2>HokoNavi Station Accessibility</h2>
      <p>Visualizing step-free paths using Leaflet and GeoJSON.</p>
      <StationMap geojsonData={sampleHokoNaviData} />
    </main>
  )
}
