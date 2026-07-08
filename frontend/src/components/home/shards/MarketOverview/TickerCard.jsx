import { formatCurrencyUSD } from '@/scripts/utils';
import { Card, CardContent } from '@/components/ui/card';


export default function TickerCard({ ticker }) {
    const { ticker: symbol, company_name, current_price, pct_change } = ticker;
    const isPositive = pct_change >= 0;
    //company_name: "Invesco QQQ Trust"
    //​​current_price: 709.43
    //​​pct_change: -1.85
    //prev_close: 722.82
    //region: "USA Nasdaq"​​
    //ticker: "QQQ"
    const tickerOverrides = {
    'GC=F': 'Gold',
    'HG=F': 'Copper',
    'CL=F': 'Oil',
    };
    let symbolOverride = null;
    if (Object.hasOwn(tickerOverrides, symbol)) {
        symbolOverride = tickerOverrides[symbol];
    };
    return (
        <Card>
            <CardContent className="flex flex-col gap-1">
                <div className="flex items-center justify-between">
                    <span className="font-medium">{symbolOverride || symbol}</span>
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
