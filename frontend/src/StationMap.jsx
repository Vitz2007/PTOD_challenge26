import React from 'react';
import {MapContainer, TileLayer, GeoJSON} from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './MapStyles.css';

export default function StationMap({geojsonData}) {
    // Centering around Tokyo Station for now
    const tokyoStationCoords = [35.6812, 139.7671];

    // Function to style the GeoJSON features ie: what lines look like on the map, what steps look like or step-free paths
    const stylePath = (feature) => {
        // HokoNavi represents step-free paths with specific properties ie: rt_type for route type
        const isStepFree = feature.properties.has_stairs === 0; 

    return {
      color: isStepFree ? '#3b82f6' : '#ef4444', // Blue for good, Red for stairs
      weight: 5,
      opacity: 0.7,
    };
  };

  return (
    <div className="map-wrapper">
      <MapContainer 
        center={tokyoStationCoords} 
        zoom={16} 
        style={{ height: '600px', width: '100%' }}
      >
        {/* The Base Map (The streets and buildings) */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* The HokoNavi Pedestrian Network Data */}
        {geojsonData && (
          <GeoJSON 
            data={geojsonData} 
            style={stylePath}
          />
        )}
      </MapContainer>
    </div>
  );
}