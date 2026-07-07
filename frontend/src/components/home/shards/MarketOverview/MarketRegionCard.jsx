import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import TickerCard from './TickerCard';

export default function MarketRegionCard({ name, tickers }) {
    return (
        <Card size="sm" className="w-full min-w-0">
            <CardHeader>
                <CardTitle className="text-sm">{name}</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {tickers.map((ticker) => (
                    <TickerCard key={ticker.ticker} ticker={ticker} />
                ))}
            </CardContent>
        </Card>
    );
}
