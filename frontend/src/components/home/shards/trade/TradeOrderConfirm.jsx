import { parseResponse } from '../../../../scripts/utils';
import '../../../../styles/utilities.css'
import '../../../../styles/colors.css'
import { useState } from 'react';


export default function TradeOrderConfirm({ formData }) {
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

    async function handleResponse(res) {
        // parse response
        // handle error codes 200, 400, 404, and 500
        // return text or cause side effects.
    }

    console.log(await parseResponse(res));
    return (
        <div className='card'>
            <form onSubmit={handleSubmitTradeOrder}>
            <button type='submit'> Submit Trade</button>
            </form>
        </div>
    )
}