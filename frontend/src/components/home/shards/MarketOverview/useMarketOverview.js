import { useState, useEffect } from 'react'
import { parseResponse } from '../../../../scripts/utils.js'

export default function useMarketOverview(setLoading, setRegions) {
    const url = '/api/market_overview';

    function _sort(dataList) {
        let sorted = {};
        const regions = new Set();
        for (const i of dataList) {
            regions.add(i.region.split(' ')[0]);
        };
        for (const i of regions) {
            sorted[i] = [];
        };
        for (const i of dataList) {
            sorted[i.region.split(' ')[0]].push(i);
        }
        return sorted
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