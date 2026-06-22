import { useState, useEffect } from 'react'
import { parseResponse } from '../../../../scripts/utils.js'

export default function useMarketOverview(setLoading, setRegions) {
    const url = '/api/market_overview';

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
            const res = await fetch(url);
            const data = await parseResponse(res);
            const dataList = data?.data;
            const sorted = _sort(dataList);
            
            setRegions(sorted);
            setLoading(false);
        }
        fetchData();
    }, [])
}