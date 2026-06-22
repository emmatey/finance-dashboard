import { useEffect, useState } from 'react';
import { parseResponse } from '../../../../scripts/utils';
import useMarketOverview from './useMarketOverview.js'

import MarketRegion from './MarketRegion';
import MarketOverviewSkeleton from './MarketOverviewSkeleton';


export default function MarketOverviewShard() {
    const [loading, setLoading] = useState(true);
    const [regions, setRegions] = useState({});    
    const regionEntries = Object.entries(regions);

    useMarketOverview(setLoading, setRegions);
    console.log(regions);

    // While loading, or if the fetch failed/returned nothing, hold the bar's
    // shape with empty frames rather than collapsing the layout.
    if (loading || regionEntries.length === 0) {
        return <MarketOverviewSkeleton />;
    }

    return (
        <div>
            {regionEntries.map(([region, packets]) => (
                <MarketRegion key={region} region={region} packets={packets} />
            ))}
        </div>
    );
}