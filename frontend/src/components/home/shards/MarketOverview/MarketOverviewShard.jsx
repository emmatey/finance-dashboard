import useMarketOverview from './useMarketOverview.js'
import MarketRegionCard from './MarketRegionCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Spinner } from '@/components/ui/spinner';
import getDisplayName from './overviewRegions.js';


function sortByRegionKey(data) {
    const regionMap = new Map();
    for (const obj of data) {
        if (typeof(obj?.region) === 'string') {
            const displayName = getDisplayName(obj.region);
            if (regionMap.has(displayName)) {
                regionMap.get(displayName).push(obj);
            } else {
                regionMap.set(displayName, [obj])
            };
        } else {
            console.warn(`Type of obj.region not str ${typeof(obj?.region)}`);
            continue;
        };
    }
    return regionMap;
};

export default function MarketOverviewShard() {
    const { loading, data, error } = useMarketOverview();
    const tickers = data ?? [];

    if (error) {
        return (<p className="text-sm text-destructive">{error}</p>)
    };

    if (loading || tickers.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Market Overview</CardTitle>
                </CardHeader>
                <CardContent className="flex items-center justify-center py-12">
                    <Spinner className="size-6" />
                </CardContent>
            </Card>
        );
    };
    const regionMap = sortByRegionKey(data);
    console.log(regionMap);
    return (
        <Card>
        </Card>
    );
}
