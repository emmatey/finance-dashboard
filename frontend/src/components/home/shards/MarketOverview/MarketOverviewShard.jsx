import { useEffect, useState } from 'react';
import { parseResponse } from '@/scripts/utils';
import useMarketOverview from './useMarketOverview.js'

import MarketRegion from './MarketRegion';
import MarketOverviewSkeleton from './MarketOverviewSkeleton';


export default function MarketOverviewShard() {
    const [loading, setLoading] = useState(true);
    const [regions, setRegions] = useState({});    

    useMarketOverview(setLoading, setRegions);

    if (loading || regionEntries.length === 0) {
        return <MarketOverviewSkeleton />;
    }

    return (
        <div>
            
        </div>
    );
}