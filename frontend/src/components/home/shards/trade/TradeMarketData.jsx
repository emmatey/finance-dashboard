import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';

export default function TradeMarketData({ activeQuery, loading, tickerInfoJson }) {
    // Utility formatters for clean UI
    const currencyFormatter = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 2
    });

    const compactFormatter = new Intl.NumberFormat("en-US", {
        notation: "compact",
        compactDisplay: "short"
    });

    const percentFormatter = new Intl.NumberFormat("en-US", {
        style: "percent",
        maximumFractionDigits: 2
    });

    if (loading) {
        return (
            <div style={{ marginTop: '20px' }}>
                <p style={{ color: 'var(--color-text-muted)' }}>Loading market data...</p>
            </div>
        );
    }

    if (!activeQuery) {
        return (
            <div style={{ marginTop: '20px' }}>
                <p style={{ color: 'var(--color-text-muted)' }}>Search for an asset above.</p>
            </div>
        );
    }

    if (!tickerInfoJson || tickerInfoJson.error) {
        return (
            <div style={{ marginTop: '20px' }}>
                <p style={{ color: 'var(--color-text-muted)' }}>No market data found for this ticker.</p>
            </div>
        );
    }

    // Smart fallback for P/E Ratio (Prefer Trailing, fallback to Forward)
    const peRatio = tickerInfoJson.trailing_pe || tickerInfoJson.forward_pe;
    const peLabel = tickerInfoJson.trailing_pe ? "P/E (TTM)" : "P/E (Fwd)";

    return (
        <div>
            <h3 style={{ margin: '0 0 4px 0', color: 'var(--color-text-main)' }}>
                {tickerInfoJson.name} ({tickerInfoJson.ticker})
            </h3>
            
            <h2 style={{ margin: '0 0 16px 0', display: 'flex', alignItems: 'baseline', gap: '8px', color: 'var(--color-text-main)' }}>
                {currencyFormatter.format(tickerInfoJson.current_price || 0)}
                <span style={{
                    fontSize: '1rem',
                    color: tickerInfoJson.pct_change_since_close >= 0 ? 'var(--color-gain)' : 'var(--color-loss)'
                }}>
                    {tickerInfoJson.pct_change_since_close >= 0 ? '▲ +' : '▼ '}
                    {tickerInfoJson.pct_change_since_close}%
                </span>
            </h2>

            {/* 2-Column Metric Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px 24px', fontSize: '0.85rem' }}>
                
                {/* Column 1: Trading Activity & Risk */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>Prev Close</span>
                        <strong style={{ color: 'var(--color-text-main)' }}>{currencyFormatter.format(tickerInfoJson.prev_close || 0)}</strong>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>Open</span>
                        <strong style={{ color: 'var(--color-text-main)' }}>{currencyFormatter.format(tickerInfoJson.market_open || 0)}</strong>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>Volume</span>
                        <strong style={{ color: 'var(--color-text-main)' }}>
                            {tickerInfoJson.todays_volume ? compactFormatter.format(tickerInfoJson.todays_volume) : 'N/A'}
                        </strong>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>Beta</span>
                        <strong style={{ color: 'var(--color-text-main)' }}>{tickerInfoJson.beta?.toFixed(2) || 'N/A'}</strong>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>52W High</span>
                        <strong style={{ color: 'var(--color-text-main)' }}>{currencyFormatter.format(tickerInfoJson.fifty_two_week_high || 0)}</strong>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>52W Low</span>
                        <strong style={{ color: 'var(--color-text-main)' }}>{currencyFormatter.format(tickerInfoJson.fifty_two_week_low || 0)}</strong>
                    </div>
                </div>

                {/* Column 2: Valuation & Consensus */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>Mkt Cap</span>
                        <strong style={{ color: 'var(--color-text-main)' }}>
                            {tickerInfoJson.market_cap ? compactFormatter.format(tickerInfoJson.market_cap) : 'N/A'}
                        </strong>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>{peLabel}</span>
                        <strong style={{ color: 'var(--color-text-main)' }}>{peRatio?.toFixed(2) || 'N/A'}</strong>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>EPS</span>
                        <strong style={{ color: 'var(--color-text-main)' }}>{tickerInfoJson.eps?.toFixed(2) || 'N/A'}</strong>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>Div Yield</span>
                        <strong style={{ color: 'var(--color-text-main)' }}>
                            {tickerInfoJson.dividend_yield ? percentFormatter.format(tickerInfoJson.dividend_yield) : 'N/A'}
                        </strong>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>Target Price</span>
                        <strong style={{ color: 'var(--color-text-main)' }}>
                            {tickerInfoJson.target_price ? currencyFormatter.format(tickerInfoJson.target_price) : 'N/A'}
                        </strong>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                        <span style={{ color: 'var(--color-text-muted)' }}>Rating</span>
                        <strong style={{ 
                            color: 'var(--color-text-main)', 
                            textTransform: 'uppercase',
                            fontWeight: 'bold'
                        }}>
                            {tickerInfoJson.rating || 'N/A'}
                        </strong>
                    </div>
                </div>

            </div>
        </div>
    );
}