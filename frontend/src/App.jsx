import React, { useState } from 'react';
import StationMap from './StationMap';
import StationDetail from './StationDetail';
import { useMapStations, useOperators, useStationFacilities } from './hooks/useStationData';

// Busy levels from the backend; 'none' = stations without a passenger survey
const BUSY_LEVELS = ['busy', 'normal', 'quiet', 'none'];

// Sample GeoJSON data for testing related purposes showing path outside Tokyo Station
const sampleHokoNaviData = {
    "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": { "has_stairs": 0, "name": "Accessible Path A" },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [139.7671, 35.6812],
          [139.7680, 35.6820]
        ]
      }
    }
  ]
};

function App() {
  // Inputs
  const [operator, setOperator] = useState('JR-East');
  const [levels, setLevels] = useState(BUSY_LEVELS); // busy levels to show
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState(null); // properties of the clicked or searched station
  const [focusStation, setFocusStation] = useState(null); // station feature the map flies to
  const [searchError, setSearchError] = useState(null);

  const { data: operators } = useOperators();
  const { data: stations, isLoading } = useMapStations(operator);
  const { data: facilities } = useStationFacilities(operator);

  // Real step-free paths from the backend when it has them, otherwise the sample data
  const paths = facilities?.features?.length ? facilities : sampleHokoNaviData;

  // Only the stations whose busy level is ticked
  const visibleStations = stations && {
    ...stations,
    features: stations.features.filter((f) => levels.includes(f.properties.busy_level ?? 'none')),
  };

  const changeOperator = (event) => {
    setOperator(event.target.value);
    setSelected(null);
    setSearch('');
  };

  const toggleLevel = (level) => {
    setLevels((current) => (current.includes(level) ? current.filter((l) => l !== level) : [...current, level]));
  };

  const searchStation = (event) => {
    event.preventDefault();
    const query = search.trim().toLowerCase();
    const match = stations?.features.find(
      (f) => f.properties.name_en?.toLowerCase() === query || f.properties.name_ja === search.trim()
    );
    setSearchError(match ? null : `No ${operator} station called "${search}"`);
    if (match) {
      setSelected(match.properties);
      setFocusStation(match);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>HokoNavi Station Accessibility</h1>
      <p>Visualizing step-free paths using Leaflet and GeoJSON.</p>
      
      {/* Input: operator */}
      <label>
        Operator{' '}
        <select value={operator} onChange={changeOperator}>
          {operators?.map((o) => (
            <option key={o.code} value={o.code}>{o.name}</option>
          ))}
        </select>
      </label>

      {/* Input: station search (suggestions come from the operator's stations) */}
      <form onSubmit={searchStation}>
        <label>
          Station{' '}
          <input list="station-names" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="e.g. Shibuya" />
        </label>
        <datalist id="station-names">
          {stations?.features.map((f) => (
            <option key={f.properties.name} value={f.properties.name_en} />
          ))}
        </datalist>
        <button type="submit">Find</button>
        {searchError && <p>{searchError}</p>}
      </form>

      {/* Input: busy-level filter */}
      <fieldset>
        <legend>Show stations</legend>
        {BUSY_LEVELS.map((level) => (
          <label key={level}>
            <input type="checkbox" checked={levels.includes(level)} onChange={() => toggleLevel(level)} />
            {level === 'none' ? 'no data' : level}{' '}
          </label>
        ))}
      </fieldset>

      {/* Output: how many stations are on the map */}
      <p>
        {isLoading ? 'Loading stations...' : `Showing ${visibleStations?.features.length ?? 0} of ${stations?.features.length ?? 0} stations`}
      </p>

      {/* Pass the data into the map! */}
      <StationMap
        geojsonData={paths}
        stations={visibleStations}
        onStationSelect={setSelected}
        operator={operator}
        focusStation={focusStation}
      />

      {selected && <StationDetail operator={selected.operator} name={selected.name} />}
    </div>
  );
}

export default App;
