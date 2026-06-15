import { parseResponse } from '../../../../scripts/utils';
import '../../../../styles/utilities.css'
import '../../../../styles/colors.css'
import { useState } from 'react';


export default function TradeOrderForm({ tickerInfoJson, setShowConfirmationScreen }) {
    // Three stateful objects
    // 1. buy / sell.

    // 2. Shares / Dollars
    // Requires data about price per share, from tickerInfoJson
    // If shares submit as normal qty = share qty
    // If dollars do math

    // 3. Qty selector
    // Send value data up to a useState onChange

    // 4. Submit
    // request will be a POST to /api/trade
    // in the request body i will specify
    // ticker, qty, and transaction_type
    // has to handle 200, 400, 404, and 500
    const [txUnit, setTxUnit] = useState('shares');
    let currentPrice = null;
    let ticker = null;
    if (tickerInfoJson) {
        currentPrice = tickerInfoJson.current_price;
        ticker = tickerInfoJson.ticker;
    };

    function handleQtyUnit(qtyUnit, qty, currentPrice) {
        // Convert dollars to shares.
        if (qtyUnit === 'dollars') {
            return qty / currentPrice;
        } else if (qtyUnit === 'shares') {
            return qty;
        } else {
            return 0;
        }
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
