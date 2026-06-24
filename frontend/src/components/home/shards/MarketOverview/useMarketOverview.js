import { useState, useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'

export default function useMarketOverview() {
    const url = '/api/market_overview';
    const [loading, setLoading] = useState(true)
    const [regions, setRegions] = useState({})

    function _sort(dataList) {
        // data.region could be a word like Oil, a country like USA, or a country
        // specific market like USA NASDAQ
        let sorted = {};
        for (const i of dataList) {
            let split = String(i?.region || '').split(' ');

            if (Object.hasOwn(sorted, split[0])) {
                sorted[split[0]].push(i);
            } else{
                sorted[split[0]] = [i];
            };
        }
        return sorted;
    }

    useEffect(() => {
        async function fetchData() {
            try {
                const res = await fetch(url);
                const data = await parseResponse(res);
                const dataList = data?.data ?? [];
                const sorted = _sort(dataList);
                setRegions(sorted);
                setLoading(false);
            } catch (error) {
                console.error(error);
                setLoading(false);
            }
        }
        fetchData();
    }, [])

    return { loading, regions }
}