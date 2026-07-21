import { Badge } from '@/components/ui/badge';
import { Spinner } from '@/components/ui/spinner';
import { formatCurrencyUSD, formatPercent, getMarketStateBadge } from '@/scripts/utils';

function MetricRow({ label, value }) {
    return (
        <div className="flex items-center justify-between border-b border-border pb-1">
            <span className="text-muted-foreground">{label}</span>
            <strong className="font-medium text-foreground">{value}</strong>
        </div>
    );
}

export default function TradeMarketData({ activeQuery, loading, tickerInfoJson }) {
    const compactFormatter = new Intl.NumberFormat("en-US", {
        notation: "compact",
        compactDisplay: "short"
    });

    if (loading) {
        return (
            <div className="mt-5 flex items-center gap-2 text-sm text-muted-foreground">
                <Spinner className="size-4" />
                Loading market data...
            </div>
        );
    }

    if (!activeQuery) {
        return (
            <p className="mt-5 text-sm text-muted-foreground">Search for an asset above.</p>
        );
    }

    if (!tickerInfoJson || tickerInfoJson.error) {
        return (
            <p className="mt-5 text-sm text-muted-foreground">No market data found for this ticker.</p>
        );
    }

    // Smart fallback for P/E Ratio (Prefer Trailing, fallback to Forward)
    const peRatio = tickerInfoJson.trailing_pe || tickerInfoJson.forward_pe;
    const peLabel = tickerInfoJson.trailing_pe ? "P/E (TTM)" : "P/E (Fwd)";
    const marketStateBadge = getMarketStateBadge(tickerInfoJson.market_state);

    return (
        <div className="mt-5 text-sm">
            <h3 className="mb-1 text-muted-foreground">
                {tickerInfoJson.name} ({tickerInfoJson.ticker})
            </h3>

            <div className="mb-4 flex items-baseline gap-2">
                <span className="text-2xl font-semibold">
                    {formatCurrencyUSD(tickerInfoJson.current_price)}
                </span>
                <span className={tickerInfoJson.pct_change_since_close >= 0 ? 'text-gain' : 'text-destructive'}>
                    {tickerInfoJson.pct_change_since_close >= 0 ? '▲ +' : '▼ '}
                    {tickerInfoJson.pct_change_since_close}%
                </span>
                {marketStateBadge && (
                    <Badge variant={marketStateBadge.variant}>{marketStateBadge.label}</Badge>
                )}
            </div>

            <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                <div className="flex flex-col gap-3">
                    <MetricRow label="Prev Close" value={formatCurrencyUSD(tickerInfoJson.prev_close)} />
                    <MetricRow label="Open" value={formatCurrencyUSD(tickerInfoJson.market_open)} />
                    <MetricRow
                        label="Volume"
                        value={tickerInfoJson.todays_volume ? compactFormatter.format(tickerInfoJson.todays_volume) : 'N/A'}
                    />
                    <MetricRow label="Beta" value={tickerInfoJson.beta?.toFixed(2) || 'N/A'} />
                    <MetricRow label="52W High" value={formatCurrencyUSD(tickerInfoJson.fifty_two_week_high)} />
                    <MetricRow label="52W Low" value={formatCurrencyUSD(tickerInfoJson.fifty_two_week_low)} />
                </div>

                <div className="flex flex-col gap-3">
                    <MetricRow
                        label="Mkt Cap"
                        value={tickerInfoJson.market_cap ? compactFormatter.format(tickerInfoJson.market_cap) : 'N/A'}
                    />
                    <MetricRow label={peLabel} value={peRatio?.toFixed(2) || 'N/A'} />
                    <MetricRow label="EPS" value={tickerInfoJson.eps?.toFixed(2) || 'N/A'} />
                    <MetricRow
                        label="Div Yield"
                        value={tickerInfoJson.dividend_yield ? formatPercent(tickerInfoJson.dividend_yield) : 'N/A'}
                    />
                    <MetricRow
                        label="Target Price"
                        value={tickerInfoJson.target_price ? formatCurrencyUSD(tickerInfoJson.target_price) : 'N/A'}
                    />
                    <MetricRow label="Rating" value={<span className="font-bold uppercase">{tickerInfoJson.rating || 'N/A'}</span>} />
                </div>
            </div>
        </div>
    );
}
