import { formatCurrencyUSD } from '@/scripts/utils.js'
import { Spinner } from '@/components/ui/spinner';
import { Button } from '@/components/ui/button';

export default function ResearchHeader({ quote, financialMetrics }) {

    if (!quote || quote.length === 0) {
        return (
            <div className="flex w-full items-center justify-center p-10">
                <Spinner className="size-6" />
            </div>
        );
    }

    const {
        ticker,
        company_name: companyName,
        exchange,
        quote_type: quoteType,
        last_price: lastPrice
    } = quote[0];
    const metrics = financialMetrics?.[0];

    return (
        <div className="flex items-end justify-between gap-4">
            <div>
                <div className="mb-1 leading-tight">
                    <span className="text-lg font-bold">{ticker}</span>
                    <span className="ml-2 text-muted-foreground">
                        {companyName}
                        {exchange ? ` · ${exchange}` : ''}
                        {quoteType ? ` · ${quoteType}` : ''}
                    </span>
                </div>
                <div className="flex items-baseline gap-3">
                    <span className="text-3xl font-bold">{lastPrice != null ? formatCurrencyUSD(lastPrice) : '—'}</span>
                    {metrics && (
                        <span className="text-sm text-muted-foreground">
                            Open {formatCurrencyUSD(metrics.market_open)}
                            <span className="mx-2">·</span>
                            Prev Close {formatCurrencyUSD(metrics.prev_close)}
                        </span>
                    )}
                </div>
            </div>
            <div className="flex gap-2">
                <Button>Buy</Button>
                <Button variant="outline">Sell</Button>
            </div>
        </div>
    );
}
