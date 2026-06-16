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

    // Array map configuration to group layouts logically and eliminate HTML boilerplate
    const displayMetrics = [
        { value: txTicker, label: "Ticker Symbol", isMoney: false, precision: null },
        { value: txType, label: "Transaction Type", isMoney: false, precision: null },
        { value: txUnit, label: "Per Share Price", isMoney: true, precision: 2 },
        { value: txShareQty, label: "Shares Quantity", isMoney: false, precision: 4 },
        { value: txDollarQty, label: "Total Estimated Cost", isMoney: true, precision: 2 },
    ];

    return (
        <form onSubmit={handleSubmitTradeOrder} class="confirmation-card-container">
            <h2>Confirm Your Transaction</h2>

            {/* Content Group Layout */}
            <div class="card-body-grid">
                {displayMetrics.map((metric, index) => {
                    // Quick logic formatting for numbers vs regular text strings
                    const formattedValue = metric.precision 
                        ? Number(metric.value).toFixed(metric.precision) 
                        : metric.value;

                    return (
                        <div key={index} class="info-card-group">
                            <strong class="card-value">
                                {metric.isMoney ? `$${formattedValue}` : formattedValue}
                            </strong>
                            <br />
                            <small class="card-caption">{metric.label}</small>
                        </div>
                    );
                })}
            </div>

            <input type="hidden" name="txTicker" value={txTicker} />
            <input type="hidden" name="txType" value={txType} />
            <input type="hidden" name="txUnit" value={txUnit} />
            <input type="hidden" name="txShareQty" value={txShareQty} />
            <input type="hidden" name="txDollarQty" value={txDollarQty} />

            <div class="card-actions-row">
                <button type="button" class="btn-cancel">Cancel</button>
                <button type="submit" class="btn-confirm">Confirm Trade</button>
            </div>
        </form>
    );
}