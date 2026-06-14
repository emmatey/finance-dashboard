import '../../../../styles/utilities.css'
import '../../../../styles/colors.css'


export default function TradeOrderForm({ activeQuery, tickerInfoJson }) {
    const []
    // Three stateful objects
    // 1. buy / sell.
        // can be handled with one bool in state.

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

    function handleSubmitTradeOrder(event) {
        event.preventDefault();
        // Makes a POST request to the '/api/trade' route.

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
