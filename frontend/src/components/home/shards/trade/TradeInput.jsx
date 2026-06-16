import { parseResponse } from '../../../../scripts/utils';
import { useState } from 'react';
import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';

export default function TradeOrderConfirm({ pendingOrder }) {
    const { txTicker, txType, txShareQty, txDollarQty, txUnit } = pendingOrder;

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

    return (
        <form onSubmit={handleSubmitTradeOrder}>
            <h2>Confirm Your Transaction</h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', margin: '16px 0' }}>
                
                <div className="card">
                    <strong>{txTicker}</strong>
                    <br />
                    <small>Ticker Symbol</small>
                </div>

                <div className="card">
                    <strong>{txType}</strong>
                    <br />
                    <small>Transaction Type</small>
                </div>

                <div className="card">
                    <strong>${txUnit}</strong>
                    <br />
                    <small>Per Share Price</small>
                </div>

                <div className="card">
                    <strong>{txShareQty}</strong>
                    <br />
                    <small>Shares Quantity</small>
                </div>

                <div className="card">
                    <strong>${txDollarQty}</strong>
                    <br />
                    <small>Total Estimated Cost</small>
                </div>
                
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
                <button type="button">Cancel</button>
                <button type="submit">Confirm Trade</button>
            </div>
        </form>
    );
}