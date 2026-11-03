import { useState } from 'react'
import StationDetail from './components/StationDetail'
import StationSearch from './components/StationSearch'

export default function App() {
  const [station, setStation] = useState(null)

  return (
    <main>
      <h1>Low-burden Mode Accessibility</h1>
      <p>Look up a station to see how busy it is and whether its lines are running normally.</p>

      <StationSearch onSelect={setStation} />

      {station && <StationDetail operator={station.operator} name={station.name} />}
    </main>
  )
}
