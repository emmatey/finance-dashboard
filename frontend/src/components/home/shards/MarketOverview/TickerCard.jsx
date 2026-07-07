import { formatCurrencyUSD } from '@/scripts/utils';
import { Card, CardContent } from '@/components/ui/card';

export default function TickerCard({ ticker, title=null }) {
    const { ticker: symbol, company_name, current_price, pct_change } = ticker;
    const isPositive = pct_change >= 0;
    //company_name: "Invesco QQQ Trust"
    //​​current_price: 709.43
    //​​pct_change: -1.85
    //prev_close: 722.82
    //region: "USA Nasdaq"​​
    //ticker: "QQQ"
    return (
        <Card size="sm" className="w-full min-w-0">
            <CardContent className="flex flex-col gap-1">
                <div className="flex items-center justify-between">
                    <span className="font-medium">{title || symbol}</span>
                    <span className={isPositive ? 'text-gain' : 'text-destructive'}>
                        {isPositive ? '▲' : '▼'} {Math.abs(pct_change).toFixed(2)}%
                    </span>
                </div>
                <span className="truncate text-xs text-muted-foreground">{company_name}</span>
                <span className="text-lg font-semibold">{formatCurrencyUSD(current_price)}</span>
            </CardContent>
        </Card>
    );
}
