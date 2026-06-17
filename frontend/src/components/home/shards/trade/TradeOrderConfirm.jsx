import { parseResponse } from '../../../../scripts/utils';
import { useState } from 'react';
import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';

export default function TradeOrderConfirm() {
    const pendingOrder = { // STUB
        txTicker: "MSFT",
        txType: "buy",
        txShareQty: 10,
        txDollarQty: 123.34
    };
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

        console.log(await parseResponse(res));
    }

    function handleCancelTx() {

    }

    return (
        <form onSubmit={handleSubmitTradeOrder} class='card'>
            <h2>Confirm Your Transaction</h2>
            <form>
                <section>

                    <figure>
                        <output> {txTicker} </output>
                        <figcaption> Company being traded. </figcaption>
                    </figure>

                    <figure>
                        <output> {txType} </output>
                        <figcaption> Transaction Type </figcaption>
                    </figure>

                    <figure>
                        <output> You are trading {txShareQty} shares for a total value of {txDollarQty} USD. </output>
                        <figcaption> test </figcaption>
                    </figure>

                </section>

                <div class='card'>
                    <button type="submit"> Submit Transaction </button>
                    <button type="button" onClick={handleCancelTx}> Cancel Transaction </button>
                </div>
            </form>
        </form>
    );
}