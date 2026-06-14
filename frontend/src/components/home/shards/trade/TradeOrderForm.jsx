import { parseResponse } from '../../../../scripts/utils';
import '../../../../styles/utilities.css'
import '../../../../styles/colors.css'


export default function TradeOrderForm({ tickerInfoJson }) {
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

    async function handleSubmitTradeOrder(event) {
        // Makes a POST request to the '/api/trade' route
        event.preventDefault();
        const formData = new FormData(event.target);

        const transactionType = formData.get('txType');
        const qtyUnit = formData.get('qtyUnit');
        const rawQty = formData.get('qtyInput');
        const qty = handleQtyUnit(qtyUnit, rawQty, currentPrice);

        if (!qty || !ticker || !transactionType) {
            console.warn("Missing data for request...");
            console.log(`qty: ${qty} ticker:${ticker}, transactionType: ${transactionType}`);
            return;
        };

        if (qty < 1 && qtyUnit === 'dollars') {
            
        }

        const res = await fetch("/api/trade", {
            method: "POST",
            headers: { "Content-Type": "application/json", },
            body: JSON.stringify({
                'ticker': ticker,
                'qty': qty,
                'transaction_type': transactionType
            })
        });

        console.log(await parseResponse(res));

    }
    return (
        <form name='tradeTransactForm' onSubmit={handleSubmitTradeOrder}>
            <select name='txType'>
                <option value='buy'>Buy</option>
                <option value='sell'>Sell</option>
            </select>
            <div>
                <input type='number' name='qtyInput' placeholder='Qty' min='0.1' step='0.1' />
                <select name='qtyUnit'>
                    <option value='shares'>Shares</option>
                    <option value='dollars'>Dollars</option>
                </select>
            </div>
            <button type='submit'>Submit</button>
        </form>
    )
}
