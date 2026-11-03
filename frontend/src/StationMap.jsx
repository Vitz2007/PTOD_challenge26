import React, {useState} from 'react';
import {MapContainer, TileLayer, GeoJSON} from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './MapStyles.css';

export default function StationMap({geojsonData}) {

    // Check whether Zen Mode is enabled or not
    const [isZenMode, setIsZenMode] = useState(false);
    // Centering around Tokyo Station for now
    const tokyoStationCoords = [35.6812, 139.7671];

    // Function to style the GeoJSON features ie: what lines look like on the map, what steps look like or step-free paths
    const stylePath = (feature) => {
        // HokoNavi represents step-free paths with specific properties ie: rt_type for route type
        const isStepFree = feature.properties.has_stairs === 0;

        if (isZenMode) {
      return {
        color: isStepFree ? '#00ffff' : '#333333', // Neon cyan for safe, dark gray for stairs
        weight: isStepFree ? 6 : 2,
        opacity: isStepFree ? 1 : 0.2,
        className: isStepFree ? 'glowing-path' : ''
      };
    } else {
      // Standard daylight colors
      return {
      color: isStepFree ? '#3b82f6' : '#ef4444', // Blue for good, Red for stairs
      weight: 5,
      opacity: 0.7,
    };
   }
  };

  return (
    <div className="map-wrapper" style={{ position: 'relative' }}>
      
      {/* The massive UI toggle button */}
      <button 
        onClick={() => setIsZenMode(!isZenMode)}
        className={`zen-toggle-btn ${isZenMode ? 'active' : ''}`}
      >
        {isZenMode ? '🌐 Exit Zen Mode' : '🧘 Activate Zen Route'}
      </button>

      <MapContainer 
        center={tokyoStationCoords} 
        zoom={16} 
        style={{ height: '600px', width: '100%' }}
      >
        {/* Toggle between standard maps and a muted dark mode map for better visibility */}
        <TileLayer
          attribution='&copy; OpenStreetMap & Carto'
          url={
            isZenMode 
              ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" 
              : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          }
        />

        {geojsonData && (
          <GeoJSON 
            // The key forces Leaflet to redraw the paths when the state changes
            key={isZenMode ? 'zen' : 'standard'} 
            data={geojsonData} 
            style={stylePath}
          />
        )}
      </MapContainer>
    </div>
  );
}