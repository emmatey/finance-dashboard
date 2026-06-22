import { parseResponse, adjustPendingOrder } from '@/scripts/utils';
import { useState } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import '@/styles/utilities.css'
import '@/styles/colors.css'


export default function TradeOrderForm({ tickerInfoJson, setPendingOrder, viewController }) {
    const [txType, setTxType] = useState("buy");
    const [txQty, setTxQty] = useState(0);
    const [txUnit, setTxUnit] = useState('shares');

    let currentPrice = null;
    let ticker = null;
    let qtyOwned = null;
    let cashBalance = null;
    if (tickerInfoJson) {
        currentPrice = tickerInfoJson.current_price;
        ticker = tickerInfoJson.ticker;
        qtyOwned = tickerInfoJson.qty_owned;
        cashBalance = tickerInfoJson.cash_balance;
    };

    function checkCanAfford(txDollarQty, cashBalance) {
        if (Number(cashBalance) >= Number(txDollarQty)) {
            return true;
        } else {
            return false
        };
    }
    // BUG FORGOT TO HANDLE THE DOLLARS STATE THIS ONLY HANDLES SHARES BUT I HAVE TO STOP
    function checkCanSell() {
        if (Number(qtyOwned) >= Number(txQty)) {
            return true;
        } else {
            return false
        };
    }

    function handleSubmit(event) {
        event.preventDefault()

        // Block submission if there's no valid quantity or active price
        if (!txQty || !currentPrice) {
            console.error(`No valid quantity or active price.`);
            return;
        };

        const [txDollarQty, txShareQty] = adjustPendingOrder(txUnit, Number(txQty), currentPrice)

        if (txType === 'sell') {
            if (!checkCanSell()) {
                toast.error("Unable to make transaction! You own less shares than you're attempting to sell!");
                return;
            };
        } else if (txType === 'buy') {
            if (!checkCanAfford(txDollarQty, cashBalance)) {
                toast.error("Unable to make transaction! You cannot afford this transaction!")
                return;
            };
        }

        setPendingOrder({
            'txTicker': ticker,
            'txType': txType,
            'txShareQty': txShareQty,
            'txDollarQty': txDollarQty,
            'txUnit': txUnit
        })
        viewController['setShowConfirmationScreen'](true);
        viewController['setShowInput'](false);
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
            <Toaster />
        </form>
    );
}