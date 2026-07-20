import { formatCurrencyUSD } from '@/scripts/utils.js'
import { Spinner } from '@/components/ui/spinner';

export default function ResearchHeader({ quote, financialMetrics }) {

    if (!quote || quote.length === 0) {
        return (
            <div className="d-flex justify-content-center align-items-center p-5 w-100">
                <Spinner />
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
        <div className="d-flex justify-content-between align-items-end mb-2">
            <div>
                <div className="lh-sm mb-1">
                    <span className="fw-bold fs-5">{ticker}</span>
                    <span className="text-muted ms-2">
                        {companyName}
                        {exchange ? ` · ${exchange}` : ''}
                        {quoteType ? ` · ${quoteType}` : ''}
                    </span>
                </div>
                <div className="d-flex align-items-baseline gap-3">
                    <span className="fw-bold fs-3">{lastPrice != null ? formatCurrencyUSD(lastPrice) : '—'}</span>
                    {metrics && (
                        <span className="text-muted small">
                            Open {formatCurrencyUSD(metrics.market_open)}
                            <span className="mx-2">·</span>
                            Prev Close {formatCurrencyUSD(metrics.prev_close)}
                        </span>
                    )}
                </div>
            </div>
            <div className="d-flex gap-2">
                <button className="btn btn-primary">Buy</button>
                <button className="btn btn-primary">Sell</button>
            </div>
        </div>
    );
}