import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';

export default function TradeMarketData({ activeQuery, loading, tickerInfoJson }) {
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

    return (
        <div style={{ marginTop: '20px' }}>
            <h3 style={{ margin: '0 0 4px 0', color: 'var(--color-text-main)' }}>
                {tickerInfoJson.name} ({tickerInfoJson.ticker})
            </h3>
            
            <h2 style={{ margin: '0 0 16px 0', display: 'flex', alignItems: 'baseline', gap: '8px', color: 'var(--color-text-main)' }}>
                ${tickerInfoJson.current_price?.toFixed(2)}
                <span style={{
                    fontSize: '1rem',
                    color: tickerInfoJson.pct_change_since_close >= 0 ? 'var(--color-gain)' : 'var(--color-loss)'
                }}>
                    {tickerInfoJson.pct_change_since_close >= 0 ? '▲ +' : '▼ '}
                    {tickerInfoJson.pct_change_since_close}%
                </span>
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.85rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>Prev Close</span>
                    <strong style={{ color: 'var(--color-text-main)' }}>${tickerInfoJson.prev_close?.toFixed(2)}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>P/E Ratio</span>
                    <strong style={{ color: 'var(--color-text-main)' }}>{tickerInfoJson.trailing_pe?.toFixed(2) || 'N/A'}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>52W High</span>
                    <strong style={{ color: 'var(--color-text-main)' }}>${tickerInfoJson.fifty_two_week_high?.toFixed(2)}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>52W Low</span>
                    <strong style={{ color: 'var(--color-text-main)' }}>${tickerInfoJson.fifty_two_week_low?.toFixed(2)}</strong>
                </div>
            </div>
        </div>
    );
}