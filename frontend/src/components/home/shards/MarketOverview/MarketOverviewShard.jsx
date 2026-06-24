import useMarketOverview from './useMarketOverview.js'

import MarketRegion from './MarketRegion';
import MarketOverviewSkeleton from './MarketOverviewSkeleton';


export default function MarketOverviewShard() {
    const { loading, regions } = useMarketOverview();

    if (loading || regionEntries.length === 0) {
        return <MarketOverviewSkeleton />;
    }

    return (
        <div>
            
        </div>
    );
}