import { parseResponse } from '../../../../scripts/utils';
import '../../../../styles/utilities.css'
import '../../../../styles/colors.css'
import { useState } from 'react';


export default function TradeOrderForm({ tickerInfoJson, setShowConfirmationScreen }) {
    const [txUnit, setTxUnit] = useState('shares');
    let currentPrice = null;
    let ticker = null;
    if (tickerInfoJson) {
        currentPrice = tickerInfoJson.current_price;
        ticker = tickerInfoJson.ticker;
    };

    function handleQtyUnit(qtyUnit, qty, currentPrice) {
        // Returns [dollars, shares]
        if (qtyUnit === 'shares') {
            const shares = Math.round(qty * 10) / 10; // Ensure it's valid 1/10th
            const dollars = Math.round(shares * currentPrice * 100) / 100; // Round to cents
            return [dollars, shares];
        }

        if (qtyUnit === 'dollars') {
            const rawShares = qty / currentPrice;
            const adjustedShares = Math.round(rawShares * 10) / 10;
            const adjustedDollars = Math.round(adjustedShares * currentPrice * 100) / 100;

            return [adjustedDollars, adjustedShares];
        }

        return [0, 0];
    }

    function handleSubmit() {

    }

    return (
        <form name='tradeTransactForm' onSubmit={handleSubmit}>
            <select name='txType'>
                <option value='buy'>Buy</option>
                <option value='sell'>Sell</option>
            </select>
            <div>
                {
                    (txUnit === 'shares')
                    &&
                    <input type='number' name='qtyInput' placeholder='Qty' min='0.1' step='0.1' />
                }
                {
                    (txUnit === 'dollars')
                    &&
                    <input type='number' name='qtyInput' placeholder='Qty' min='1' step='1' />
                }
                <select name='qtyUnit' onChange={(e) => (setTxUnit(e.target.value))}>
                    <option value='shares'>Shares</option>
                    <option value='dollars'>Dollars</option>
                </select>
            </div>
            <button type='submit'>Submit</button>
        </form>
    )
}
