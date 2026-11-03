import { useState } from 'react'
import { getOperators, getStations } from '../api/client'
import { useApi } from '../api/useApi'

// Operator picker plus station-name box with suggestions.
// Calls onSelect({ operator, name }) on submit.
export default function StationSearch({ onSelect }) {
  const [operator, setOperator] = useState('JR-East')
  const [query, setQuery] = useState('')
  const { data: operators } = useApi(getOperators, [])
  const { data: stations } = useApi(() => getStations(operator), [operator])

  // The station list has one entry per line, so remove duplicate names
  const names = [...new Set((stations || []).map((s) => s.name.en).filter(Boolean))].sort()

  function handleSubmit(event) {
    event.preventDefault()
    if (query.trim()) onSelect({ operator, name: query.trim() })
  }

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="operator">Operator</label>{' '}
      <select id="operator" value={operator} onChange={(event) => setOperator(event.target.value)}>
        {(operators || []).map((o) => (
          <option key={o.code} value={o.code}>
            {o.name}
          </option>
        ))}
      </select>{' '}
      <label htmlFor="station">Station</label>{' '}
      <input
        id="station"
        list="station-names"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="e.g. Shinjuku"
      />
      <datalist id="station-names">
        {names.map((name) => (
          <option key={name} value={name} />
        ))}
      </datalist>{' '}
      <button type="submit">Search</button>
    </form>
  )
}
