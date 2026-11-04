import React, { useState, useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './MapStyles.css';
import { STATIONS, useOverpassStation } from './hooks/useOverpassStation';

// Helps to format OSM level numbers into understandable labels (e.g., -1 -> B1F, 0 -> 1F)
const formatFloor = (lvl) => {
  const n = parseFloat(lvl);
  if (n === 0) return '1F';
  return n > 0 ? `${n + 1}F` : `B${Math.abs(n)}F`;
};

// Color coded elevation color palette
const getFloorColor = (lvl) => {
  const n = parseFloat(lvl);
  if (n === 0) return '#10b981'; // Emerald Green (Ground/Entry 1F)
  if (n > 0) return '#38bdf8';   // Sky Blue/Silver (Upper 2F+)
  if (n === -1) return '#f59e0b'; // Amber (B1F)
  if (n === -2) return '#ea580c'; // Deep Orange (B2F)
  return '#8b5cf6';               // Cool Purple (B3F-B5F+)
};

function MapCamera({ center }) {
  const map = useMap();
  map.setView(center, 17);
  return null;
}

export default function StationMap() {
  const [station, setStation] = useState('tokyo');
  const [selectedFloor, setSelectedFloor] = useState('ALL');
  const [isZenMode, setIsZenMode] = useState(false);

  const { data, isLoading } = useOverpassStation(station);

  // 0ms filtering of paths and elevators
  const { pathsGeoJSON, elevators } = useMemo(() => {
    if (!data) return { pathsGeoJSON: null, elevators: [] };
    const paths = data.features.filter(f => !f.properties.isElevator && (
      selectedFloor === 'ALL' || f.properties.levels.includes(selectedFloor)
    ));
    const elevs = data.features.filter(f => f.properties.isElevator && (
      selectedFloor === 'ALL' || f.properties.levels.includes(selectedFloor)
    ));
    return {
      pathsGeoJSON: { type: 'FeatureCollection', features: paths },
      elevators: elevs
    };
  }, [data, selectedFloor]);

  const stylePath = (feature) => {
    const isStepFree = !feature.properties.hasStairs;
    const floorColor = getFloorColor(selectedFloor === 'ALL' ? '0' : selectedFloor);
    if (isZenMode) {
      return {
        color: isStepFree ? '#00ffff' : '#333333',
        weight: isStepFree ? 6 : 2,
        opacity: isStepFree ? 1 : 0.15,
        className: isStepFree ? 'glowing-path' : ''
      };
    }
    return { color: isStepFree ? floorColor : '#ef4444', weight: 5, opacity: 0.8 };
  };

  return (
    <div className="map-wrapper">
      <MapContainer center={STATIONS[station].coords} zoom={17} style={{ height: '100vh', width: '100%' }}>
        <MapCamera center={STATIONS[station].coords} />
        <TileLayer
          url={isZenMode
            ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"}
        />

        {pathsGeoJSON && (
          <GeoJSON key={`${station}-${selectedFloor}-${isZenMode}`} data={pathsGeoJSON} style={stylePath} />
        )}

        {/* Depth-Ring Elevator Markers with 1-Tap Floor Jump Popup */}
        {elevators.map((elev) => {
          const [lon, lat] = elev.geometry.coordinates;
          const connectsToGround = elev.properties.levels.includes('0');
          const ringColor = connectsToGround ? '#10b981' : '#38bdf8';
          const fillColor = getFloorColor(selectedFloor === 'ALL' ? '0' : selectedFloor);

          const icon = L.divIcon({
            className: 'custom-elev-icon',
            html: `<div class="depth-ring-pin" style="background:${fillColor}; border-color:${ringColor}">🛗</div>`,
            iconSize: [34, 34]
          });

          return (
            <Marker key={elev.properties.id} position={[lat, lon]} icon={icon}>
              <Popup>
                <div className="elev-popup">
                  <strong>Elevator Shaft</strong>
                  <p>Tap a floor to jump:</p>
                  <div className="popup-floor-btns">
                    {elev.properties.levels.map(lvl => (
                      <button
                        key={lvl}
                        style={{ background: getFloorColor(lvl) }}
                        onClick={() => setSelectedFloor(lvl)}
                      >
                        {formatFloor(lvl)}
                      </button>
                    ))}
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Hybrid Smart Hub Card */}
      <div className="smart-hub-card">
        {/* Row 1: JR East Station Switcher */}
        <div className="station-strip">
          {Object.entries(STATIONS).map(([key, info]) => (
            <button
              key={key}
              className={`station-pill ${station === key ? 'active' : ''}`}
              onClick={() => { setStation(key); setSelectedFloor('ALL'); }}
            >
              {info.name}
            </button>
          ))}
        </div>

        {/* Row 2: Dynamic Color-Coded Floor Strip */}
        <div className="floor-strip">
          <button
            className={`floor-pill ${selectedFloor === 'ALL' ? 'active' : ''}`}
            style={{ background: selectedFloor === 'ALL' ? '#334155' : '#1e293b' }}
            onClick={() => setSelectedFloor('ALL')}
          >
            ALL
          </button>
          {isLoading ? <span className="loading-txt">Loading floors...</span> : (
            data?.floors.map((lvl) => (
              <button
                key={lvl}
                className={`floor-pill ${selectedFloor === lvl ? 'active' : ''}`}
                style={{
                  background: selectedFloor === lvl ? getFloorColor(lvl) : '#1e293b',
                  borderColor: getFloorColor(lvl)
                }}
                onClick={() => setSelectedFloor(lvl)}
              >
                {formatFloor(lvl)}
              </button>
            ))
          )}
        </div>

        {/* Row 3: One-Thumb Zen Route Toggle */}
        <button
          onClick={() => setIsZenMode(!isZenMode)}
          className={`zen-toggle-btn ${isZenMode ? 'active' : ''}`}
        >
          {isZenMode ? '🌐 Exit Zen Mode' : '🧘 Activate Zen Route'}
        </button>
      </div>
    </div>
  );
}