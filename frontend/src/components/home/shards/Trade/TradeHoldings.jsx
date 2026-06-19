import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';

export default function TradeHoldings({ tickerInfoJson }) {
    const formatter = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD"
    });

    if (!tickerInfoJson || tickerInfoJson.error) {
        return (
            <div className='card' style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '180px' }}>
                <p style={{ color: 'var(--color-text-muted)' }}>
                    Search a ticker to view your holdings.
                </p>
            </div>
        );
    }

    const { ticker, qty_owned, holding_value, cash_balance } = tickerInfoJson;

    return (
        <div className='card' style={{ height: '100%' }}>
            <h2 style={{ color: 'var(--color-text-main)' }}>Your Position</h2>
            
            <section style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
                <figure>
                    <h3 style={{ color: 'var(--color-text-main)' }}>{qty_owned || 0} shares</h3>
                    <figcaption style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>Quantity Owned</figcaption>
                </figure>

                <figure>
                    <h3 style={{ color: 'var(--color-text-main)' }}>{formatter.format(holding_value || 0)}</h3>
                    <figcaption style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>Current Value</figcaption>
                </figure>
                
                <hr style={{ width: '100%', border: 'none', borderTop: '1px solid var(--color-border)' }} />

                <figure>
                    <h3 style={{ color: 'var(--color-gain)' }}>
                        {formatter.format(cash_balance || 0)}
                    </h3>
                    <figcaption style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>Available Buying Power</figcaption>
                </figure>
            </section>
        </div>
    );
}