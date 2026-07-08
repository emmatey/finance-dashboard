import useMarketOverview from './useMarketOverview.js'
import MarketRegionCard from './MarketRegionCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import getDisplayName from './overviewRegions.js';


function sortByRegionKey(data) {
    const regionMap = new Map();
    for (const obj of data) {
        if (typeof (obj?.region) === 'string') {
            const displayName = getDisplayName(obj.region);
            if (regionMap.has(displayName)) {
                regionMap.get(displayName).push(obj);
            } else {
                regionMap.set(displayName, [obj])
            };
        } else {
            console.warn(`Type of obj.region not str ${typeof (obj?.region)}`);
            continue;
        };
    }
    return regionMap;
};

export default function MarketOverviewShard() {
    const { loading, data, error } = useMarketOverview();
    const regionMap = data ? sortByRegionKey(data) : new Map();

    const blackList = ['USA', 'Commodities'];
    const worldTickers= [];
    for (const [displayName, tickers] of regionMap.entries()) {
        if (!blackList.includes(displayName)) {
            worldTickers.push(...tickers);
        }
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Market Overview</CardTitle>
            </CardHeader>
            <CardContent>

                {loading &&
                    <Spinner className="size-6" />
                }

                {error &&
                    <p className="text-sm text-destructive">{error}</p>
                }

                {regionMap.size > 0 && <MarketRegionCard name={"USA"} tickers={regionMap.get("USA")} />}

                {worldTickers.length > 0 && <MarketRegionCard name={"World"} tickers={worldTickers} />}

                {regionMap.size > 0 && <MarketRegionCard name={"Commodities"} tickers={regionMap.get("Commodities")} />}

            </CardContent>
        </Card>
    );
}
