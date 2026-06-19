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
    const [isError, setIsError] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { txTicker, txType, txShareQty, txDollarQty } = pendingOrder;
    const formatter = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD"
    });

    async function handleSubmitTradeOrder(event) {
        event.preventDefault();
        setIsSubmitting(true);
        
        try {
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

            viewController['setShowConfirmationScreen'](false);
            viewController['setShowSummaryScreen'](true);
            setActiveQuery(null);
            setOrderSummaryData(statusJson);
        } catch (error) {
            setIsError(error.message || "An unexpected error occurred.");
        } finally {
            setIsSubmitting(false);
        }
    }

    function handleCancelTx() {
        setActiveQuery(null);
        viewController['setShowConfirmationScreen'](false);
        viewController['setShowInput'](true);
    }

    return (
        <form onSubmit={handleSubmitTradeOrder} className='card'>
            <h2>{isError ? "Transaction Failed" : "Confirm Your Transaction"}</h2>
            <hr />

            {isError ? (
                <section style={{ padding: '20px', textAlign: 'center' }}>
                    <p style={{ color: 'var(--color-loss)', fontWeight: 'bold' }}>
                        {isError}
                    </p>
                    <p>Please return to the input screen to adjust your order parameters.</p>
                </section>
            ) : (
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
                        <h3> You are trading {txShareQty} shares for a total value of {formatter.format(txDollarQty)} USD. </h3>
                        <figcaption> Price was last updated at {tickerInfoJson?.last_updated} UTC. </figcaption>
                    </figure>
                </section>
            )}

            <div className='card'>
                <button 
                    type="submit" 
                    disabled={isSubmitting || isError}
                >
                    {isSubmitting ? "Processing..." : "Submit Transaction"}
                </button>
                
                <button type="button" onClick={handleCancelTx}> 
                    {isError ? "Back to Input" : "Cancel Transaction"} 
                </button>
            </div>
        </form>
    );
}