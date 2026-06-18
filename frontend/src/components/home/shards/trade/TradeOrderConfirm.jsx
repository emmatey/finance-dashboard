import { parseResponse } from '../../../../scripts/utils';
import { useState } from 'react';
import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';

export default function TradeOrderConfirm({
    pendingOrder,
    tickerInfoJson,
    setActiveQuery,
    setOrderSummaryData,
    viewController
}) {
    const { txTicker, txType, txShareQty, txDollarQty, txUnit } = pendingOrder;
    const formatter = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD"
    });
    const txDollarQtyFormatted = formatter.format(txDollarQty);

    async function handleSubmitTradeOrder(event) {
        event.preventDefault();

        const res = await fetch("/api/trade", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                'ticker': txTicker,
                'qty': txShareQty,
                'transaction_type': txType
            })
        });

        const statusJson = await parseResponse(res);
        console.log(statusJson);
        viewController['setShowConfirmationScreen'](false);
        viewController['setShowSummaryScreen'](true);
        setActiveQuery(null);
        setOrderSummaryData(statusJson);
    }

    function handleCancelTx() {
        setActiveQuery(null);
        viewController['setShowConfirmationScreen'](false);
        viewController['setShowInput'](true);
    }

    return (
        <form onSubmit={handleSubmitTradeOrder} className='card'>
            <h2>Confirm Your Transaction</h2>
            <section>

                <figure>
                    <h3> {txTicker} </h3>
                    <figcaption> Company being traded. </figcaption>
                </figure>

                <figure>
                    <h3> {txType.toUpperCase()} </h3>
                    <figcaption> Transaction Type </figcaption>
                </figure>

                <figure>
                    <h3> You are trading {txShareQty} shares for a total value of {txDollarQty} USD. </h3>
                    <figcaption> Price was last updated at {tickerInfoJson?.last_updated} UTC. </figcaption>
                </figure>

            </section>

            <div className='card'>
                <button type="submit"> Submit Transaction </button>
                <button type="button" onClick={handleCancelTx}> Cancel Transaction </button>
            </div>
        </form>
    );
}