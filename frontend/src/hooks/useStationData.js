import { useQuery } from '@tanstack/react-query';

// Get facility data from python backend
const fetchFacilities = async (operator = 'odpt.Operator: JR East') => {
    const res = await fetch ('http://127.0.0.1:8000/facilities?operator=${operator}');
    if (!res.ok) throw new Error ('Network response was not okay');
    return res.json();
};

export const useStationFacilities = (operator) => {
    return useQuery({
        queryKey: ['facilities', operator],
        queryFn: () => fetchFacilities(operator),
    });
};