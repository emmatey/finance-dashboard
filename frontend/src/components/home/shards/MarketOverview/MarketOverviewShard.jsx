import { Fragment } from 'react'
import useMarketOverview from './useMarketOverview.js'
import MarketRegionCard from './MarketRegionCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Spinner } from '@/components/ui/spinner';
import { CATEGORY_ORDER, getMarketOverviewCategory } from './marketOverviewCategories';

const FRAME_STACK = "flex flex-col gap-3";

function groupByRegionLabel(tickers) {
    const groups = new Map();
    for (const ticker of tickers) {
        const key = String(ticker.region || '').split(' ')[0];
        if (!groups.has(key)) groups.set(key, { key, tickers: [] });
        groups.get(key).tickers.push(ticker);
    }
    return Array.from(groups.values());
}

// American markets first, everything else alphabetical by group label.
function sortRegionGroups(groups) {
    return [...groups].sort((a, b) => {
        if (a.key === 'USA') return -1;
        if (b.key === 'USA') return 1;
        return a.key.localeCompare(b.key);
    });
}

export default function MarketOverviewShard() {
    const { loading, data, error } = useMarketOverview();

    const tickers = data ?? [];

    if (error) return <p className="text-sm text-destructive">{error}</p>;

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
    }

    const categoryGroups = [...CATEGORY_ORDER, 'Other']
        .map((category) => {
            const categoryTickers = tickers.filter((ticker) => getMarketOverviewCategory(ticker.region) === category);
            const regionGroups = sortRegionGroups(groupByRegionLabel(categoryTickers));
            return { category, regionGroups };
        })
        .filter(({ regionGroups }) => regionGroups.length > 0);

    return (
        <Card>
        </Card>
    );
}
