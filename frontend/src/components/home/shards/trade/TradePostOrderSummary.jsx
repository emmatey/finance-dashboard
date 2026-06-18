import { parseResponse } from '../../../../scripts/utils';
import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';
import { useState } from 'react';

export default function TradePostOrderSummary({
    orderSummaryData,
    viewController
}) {
    const { new_balance, qty, ticker, tx_value, unit_price } = orderSummaryData || {};

    const formatter = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD"
    });

    function handleCloseSummary() {
        if (viewController) {
            viewController['setShowSummaryScreen'](false);
            viewController['setShowInput'](true);
        }
    }

    if (!orderSummaryData) {
        return (
            <div className="card">
                <p>No order details available.</p>
            </div>
        );
    }

    return (
        <div className='card'>
            <h2>Transaction Success</h2>

            <section>
                <figure>
                    <h3>{ticker}</h3>
                    <figcaption>Asset Traded</figcaption>
                </figure>

                <figure>
                    <h3>{qty} shares</h3>
                    <figcaption>Quantity Exchanged</figcaption>
                </figure>

                <figure>
                    <h3>{formatter.format(unit_price)}</h3>
                    <figcaption>Execution Price (per unit)</figcaption>
                </figure>

                <figure>
                    <h3>{formatter.format(tx_value)}</h3>
                    <figcaption>Total Transaction Value</figcaption>
                </figure>

                <figure>
                    <h3>{formatter.format(new_balance)}</h3>
                    <figcaption>Your New Remaining Balance</figcaption>
                </figure>
            </section>

            <div className='card'>
                <button type="button" onClick={handleCloseSummary}>
                    Done
                </button>
            </div>
        </div>
    );
}