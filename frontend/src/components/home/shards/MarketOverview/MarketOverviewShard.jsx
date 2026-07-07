import useMarketOverview from './useMarketOverview.js'
import MarketRegionCard from './MarketRegionCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Spinner } from '@/components/ui/spinner';
import getDisplayName from './overviewRegions.js';
import TickerCard from './TickerCard.jsx';


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
    
    const filteredMap = new Map();
    const blackList = ['USA', 'Commodities'];
    for (const [displayName, data] of regionMap.entries()) {
        if (!blackList.includes(displayName)) {
            filteredMap.set(displayName, data)
        }
    };
    let filteredMapTuples = [];
    for (const[displayName, data] of filteredMap.entries()) {
        filteredMapTuples.push([displayName, data]);
    }

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

                {filteredMapTuples.length > 0 && 
                    <div>
                        {
                        filteredMapTuples.map(
                            ([displayName, data], idx) => (data.map((tickerData) => (<TickerCard key={tickerData.ticker} ticker={tickerData} title={displayName} />))))
                        }
                    </div>
                }
                <Separator />
                {regionMap.size > 0 && <MarketRegionCard name={"Commodities"} tickers={regionMap.get("Commodities")} />}

            </CardContent>
        </Card>
    );
}
