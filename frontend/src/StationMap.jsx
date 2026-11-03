import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import {MapContainer, TileLayer, GeoJSON, useMap} from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './MapStyles.css';

// Moves the map: zooms to all stations when the operator changes, flies to a searched station
function MapFocus({ operator, stations, focusStation }) {
  const map = useMap();
  const firstOperator = useRef(operator);

  useEffect(() => {
    // Keep the starting view (Tokyo Station) until the operator is changed
    if (operator === firstOperator.current || !stations?.features?.length) return;
    map.fitBounds(L.geoJSON(stations).getBounds());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [map, operator, stations?.features?.[0]?.properties.operator]);

  useEffect(() => {
    if (!focusStation) return;
    const [lng, lat] = focusStation.geometry.coordinates;
    map.flyTo([lat, lng], 16);
  }, [map, focusStation]);

  return null;
}

export default function StationMap({geojsonData, stations, onStationSelect, operator, focusStation}) {
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

  // Stations from the backend: one small clickable circle per station.
  // Bigger circle = more passengers per day (5px with no data, about 20-24px for the busiest).
  const stationRadius = (passengers) => (passengers ? 5 + Math.sqrt(passengers) / 55 : 5);
  const stationPoint = (feature, latlng) =>
    L.circleMarker(latlng, { radius: stationRadius(feature.properties.passengers_per_day), weight: 1 });

  const onEachStation = (feature, layer) => {
    layer.bindTooltip(feature.properties.name_en);
    layer.on('click', () => onStationSelect?.(feature.properties));
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

        {/* Stations (the key redraws the layer when the data changes) */}
        {stations && (
          <GeoJSON
            key={stations.features.map((f) => f.properties.name).join()}
            data={stations}
            pointToLayer={stationPoint}
            onEachFeature={onEachStation}
          />
        )}

        <MapFocus operator={operator} stations={stations} focusStation={focusStation} />
      </MapContainer>
    </div>
  );
}