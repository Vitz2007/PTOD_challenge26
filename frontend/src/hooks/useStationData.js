import { useQuery } from '@tanstack/react-query';

// Get facility data from python backend
const fetchFacilities = async (operator = 'odpt.Operator: JR East') => {
    const res = await fetch (`http://127.0.0.1:8000/facilities?operator=${operator}`);
    if (!res.ok) throw new Error ('Network response was not okay');
    return res.json();
};

export const useStationFacilities = (operator) => {
    return useQuery({
        queryKey: ['facilities', operator],
        queryFn: () => fetchFacilities(operator),
    });
};

// Stations as GeoJSON points for the map
// properties: { operator, name, name_en, name_ja, busy_level, passengers_per_day }
const fetchMapStations = async (operator) => {
    const res = await fetch (`http://127.0.0.1:8000/api/v1/map/stations?operator=${operator}`);
    if (!res.ok) throw new Error ('Network response was not okay');
    return res.json();
};

export const useMapStations = (operator) => {
    return useQuery({
        queryKey: ['map-stations', operator],
        queryFn: () => fetchMapStations(operator),
    });
};

// One station's details: { name, operator, congestion, service_status, facilities, notes }
const fetchStation = async (operator, name) => {
    const res = await fetch (`http://127.0.0.1:8000/api/v1/stations/${operator}/${name}`);
    if (!res.ok) throw new Error ('Network response was not okay');
    return res.json();
};

export const useStation = (operator, name) => {
    return useQuery({
        queryKey: ['station', operator, name],
        queryFn: () => fetchStation(operator, name),
        enabled: Boolean(operator && name),
    });
};

// Operators the backend supports: [{ code, name }]
const fetchOperators = async () => {
    const res = await fetch (`http://127.0.0.1:8000/api/v1/operators`);
    if (!res.ok) throw new Error ('Network response was not okay');
    return res.json();
};

export const useOperators = () => {
    return useQuery({
        queryKey: ['operators'],
        queryFn: fetchOperators,
    });
};
