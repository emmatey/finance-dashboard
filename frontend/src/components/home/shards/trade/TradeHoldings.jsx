import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';

export default function TradeHoldings({ tickerInfoJson }) {
    const formatter = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD"
    });

    // If there's no active search, show a placeholder card
    if (!tickerInfoJson) {
        return (
            <div className='card' style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ color: 'var(--color-text-muted, gray)' }}>
                    Search a ticker to view your holdings.
                </p>
            </div>
        );
    }

    const { ticker, qty_owned, holding_value, cash_balance } = tickerInfoJson;

    return (
        <div className='card'>
            <h2>Your {ticker} Holdings</h2>
            <hr />
            
            <section >
                <figure>
                    <h3>{qty_owned || 0} shares</h3>
                    <figcaption>Quantity Owned</figcaption>
                </figure>

                <figure>
                    <h3>{formatter.format(holding_value || 0)}</h3>
                    <figcaption>Current Holding Value</figcaption>
                </figure>
                
                <hr/>

                <figure>
                    <h3>
                        {formatter.format(cash_balance || 0)}
                    </h3>
                    <figcaption>Available Purchasing Power</figcaption>
                </figure>
            </section>
        </div>
    );
}