import '../../../styles/utilities.css'
import '../../../styles/colors.css'

// Buy/sell order submission form. Reads the active query and its backend
// result (owned by the parent shard) so an order can be placed against the
// ticker currently shown in the search results panel.
export default function TradeOrderForm({ activeQuery, tickerInfoJson }) {
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
