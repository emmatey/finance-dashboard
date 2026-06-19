import { useEffect, useState } from 'react';
import { parseResponse } from '../../../../scripts/utils';
import MarketRegion from './MarketRegion';
import MarketOverviewSkeleton from './MarketOverviewSkeleton';
import * as styles from './styles';
import '../../../../styles/colors.css';


export default function MarketOverviewShard() {
    const [loading, setLoading] = useState(true);
    const [regions, setRegions] = useState({});

    async function fetchMarketOverview() {
        try {
            const response = await fetch('/api/market_overview', { method: 'GET' });
            const json = await parseResponse(response);
            return json.data ?? [];
        } catch (error) {
            // Fixed route + fixed params: nothing actionable to tell the user.
            // Stay silent — an API outage is evident elsewhere in the UI.
            console.error(error.message);
            return [];
        }
    }

    useEffect(() => {
        (async () => {
            const packets = await fetchMarketOverview();
            setRegions(groupByRegion(packets));
            setLoading(false);
        })();
    }, []);

    const regionEntries = Object.entries(regions);

    // While loading, or if the fetch failed/returned nothing, hold the bar's
    // shape with empty frames rather than collapsing the layout.
    if (loading || regionEntries.length === 0) {
        return <MarketOverviewSkeleton />;
    }

    return (
        <div style={styles.bar}>
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
