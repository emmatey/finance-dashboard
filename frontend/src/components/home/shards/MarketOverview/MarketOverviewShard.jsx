import useMarketOverview from './useMarketOverview.js'
import MarketRegion from './MarketRegion';
import MarketOverviewSkeleton from './MarketOverviewSkeleton';


export default function MarketOverviewShard() {
    const { loading, data, error, responseCode } = useMarketOverview();

    const regionEntries = Object.entries(data ?? {});

    if (loading || regionEntries.length === 0) return <MarketOverviewSkeleton />;
    if (error) return <p>{error}</p>;

    return (
        <div>
            {regionEntries.map(([name, items]) => (
                <MarketRegion key={name} name={name} items={items} />
            ))}
        </div>
    );
}