import { useQuery } from '@tanstack/react-query';

export const STATIONS = {
  tokyo: { name: 'Tokyo', coords: [35.6812, 139.7671], bbox: '35.676,139.762,35.686,139.772' },
  shinjuku: { name: 'Shinjuku', coords: [35.6896, 139.7006], bbox: '35.685,139.696,35.694,139.705' },
  ikebukuro: { name: 'Ikebukuro', coords: [35.7295, 139.7109], bbox: '35.725,139.706,35.734,139.715' },
  ueno: { name: 'Ueno', coords: [35.7141, 139.7774], bbox: '35.710,139.773,35.718,139.782' },
};

const fetchOverpass = async (stationKey) => {
  const { bbox } = STATIONS[stationKey];
  const query = `[out:json][timeout:25];(way["highway"~"footway|corridor|steps"]["level"](${bbox});node["highway"="elevator"](${bbox}););out body geom;`;
  const res = await fetch(`https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`);
  const data = await res.json();

  const floorSet = new Set();
  const features = data.elements.map((el) => {
    const rawLevels = (el.tags?.level || '0').split(';').map(l => l.trim());
    rawLevels.forEach(l => { if (!isNaN(parseFloat(l))) floorSet.add(l); });

    const isElevator = el.tags?.highway === 'elevator';
    const hasStairs = el.tags?.highway === 'steps' || el.tags?.stairs === 'yes';

    return {
      type: 'Feature',
      properties: { id: el.id, isElevator, hasStairs, levels: rawLevels },
      geometry: isElevator
        ? { type: 'Point', coordinates: [el.lon, el.lat] }
        : { type: 'LineString', coordinates: (el.geometry || []).map(p => [p.lon, p.lat]) }
    };
  });

  // Sort floors from highest above-ground to deepest basement
  const sortedFloors = Array.from(floorSet).sort((a, b) => parseFloat(b) - parseFloat(a));
  return { features, floors: sortedFloors.length ? sortedFloors : ['1', '0', '-1', '-2'] };
};

export const useOverpassStation = (stationKey) => useQuery({
  queryKey: ['overpass', stationKey],
  queryFn: () => fetchOverpass(stationKey),
  staleTime: 1000 * 60 * 30, // Cache for 30 mins so switching becomes instant
});