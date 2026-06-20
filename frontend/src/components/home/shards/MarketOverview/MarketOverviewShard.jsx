import { useEffect, useState } from 'react';
import { parseResponse } from '../../../../scripts/utils';
import MarketRegion from './MarketRegion';
import MarketOverviewSkeleton from './MarketOverviewSkeleton';


export default function MarketOverviewShard() {
    const [loading, setLoading] = useState(true);
    const [regions, setRegions] = useState({});



    
    const regionEntries = Object.entries(regions);

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

// Collapse per-ticker region labels ("USA S&P 500", "USA Dow") into a single
// macro region ("USA") so each container holds all of that region's tickers.
// Single-ticker regions (Africa, Gold, ...) simply form a group of one.
function groupByRegion(packets) {
    const grouped = {};
    for (const packet of packets) {
        const macro = (packet.region ?? '').split(' ')[0] || 'Other';
        if (!grouped[macro]) grouped[macro] = [];
        grouped[macro].push(packet);
    }
    return grouped;
}
