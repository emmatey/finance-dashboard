import { parseResponse } from '../../../../scripts/utils';
import { adjustPendingOrder } from '../../../../scripts/utils';
import { useState } from 'react';
import '../../../../styles/utilities.css'
import '../../../../styles/colors.css'


export default function TradeOrderForm({ tickerInfoJson, setPendingOrder }) {
    const [txType, setTxType] = useState("buy");
    const [txQty, setTxQty] = useState(0);
    const [txUnit, setTxUnit] = useState('shares');

    let currentPrice = null;
    let ticker = null;
    if (tickerInfoJson) {
        currentPrice = tickerInfoJson.current_price;
        ticker = tickerInfoJson.ticker;
    };

    function handleSubmit(event) {
        event.preventDefault()

        // Block submission if there's no valid quantity or active price
        if (!txQty || !currentPrice) return;

        const [txDollarQty, txShareQty] = adjustPendingOrder(txUnit, Number(txQty), currentPrice)
        setPendingOrder({
            'txType': txType,
            'txShareQty': txShareQty,
            'txDollarQty': txDollarQty,
            'txUnit': txUnit
        })
    }

    return (
        <form name='tradeTransactForm' onSubmit={handleSubmit}>
            <select name='txType' value={txType} onChange={(e) => setTxType(e.target.value)}>
                <option value='buy'>Buy</option>
                <option value='sell'>Sell</option>
            </select>

            <div>
                <input
                    type='number'
                    name='qtyInput'
                    placeholder={txUnit === 'shares' ? 'Qty of Shares' : 'Amount in USD'}
                    value={txQty} 
                    onChange={(e) => setTxQty(e.target.value)}
                    min={txUnit === 'shares' ? '0.1' : '1'}
                    step={txUnit === 'shares' ? '0.1' : '1'}
                />

                <select name='qtyUnit' value={txUnit} onChange={(e) => setTxUnit(e.target.value)}>
                    <option value='shares'>Shares</option>
                    <option value='dollars'>Dollars</option>
                </select>
            </div>

            {/* Disable button if there's no active ticker info available */}
            <button type='submit' disabled={!tickerInfoJson}>Submit</button>
        </form>
    );
}