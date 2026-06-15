import { parseResponse } from '../../../../scripts/utils';
import { adjustPendingOrder } from '../../../../scripts/utils';
import '../../../../styles/utilities.css'
import '../../../../styles/colors.css'
import { useState } from 'react';


export default function TradeOrderForm({ tickerInfoJson, setPendingOrder }) {
    const [txType, setTxType] = useState(null);
    const [txQty, setTxQty] = useState(0);
    const [txUnit, setTxUnit] = useState('shares');

    let currentPrice = null;
    let ticker = null;
    if (tickerInfoJson) {
        currentPrice = tickerInfoJson.current_price;
        ticker = tickerInfoJson.ticker;
    };

    function handleSubmit() {
        const [txDollarQty, txShareQty] = adjustPendingOrder(txType, txQty, currentPrice)
        setPendingOrder({
            'txType': txType,
            'txShareQty': txShareQty,
            'txDollarQty': txDollarQty,
            'txUnit': txUnit
        })
    }

    return (
        <form name='tradeTransactForm' onSubmit={handleSubmit}>
            <select name='txType' onChange={(e) => (setTxType(e.target.value))}>
                <option value='buy'>Buy</option>
                <option value='sell'>Sell</option>
            </select>
            <div>
                {
                    (txUnit === 'shares')
                    &&
                    <input type='number' name='qtyInput' placeholder='Qty' onChange={(e) => setTxQty(e.target.value)} min='0.1' step='0.1' />
                }
                {
                    (txUnit === 'dollars')
                    &&
                    <input type='number' name='qtyInput' placeholder='Qty' onChange={(e) => setTxQty(e.target.value)} min='1' step='1' />
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