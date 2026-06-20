import { useState, useEffect } from "react";


export default function useFetchHoldings() {
    async function fetchMarketOverview() {
        try {
            const response = await fetch('/api/market_overview', { method: 'GET' });
            const json = await parseResponse(response);
            return json.data ?? [];
        } catch (error) {
            console.error(error.message);
            return [{
                'loading': false,
                'regions': []
            }];
        }
    }

    useEffect(() => {
        (async () => {
            const packets = await fetchMarketOverview();
            setRegions(groupByRegion(packets));
            setLoading(false);
        })();
    }, []);


    return (
        null
    )
}