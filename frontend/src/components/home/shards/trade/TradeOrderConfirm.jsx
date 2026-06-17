import { parseResponse } from '../../../../scripts/utils';
import { useState } from 'react';
import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';

export default function TradeOrderConfirm() {
    const tickerInfoJson = {
        "success": true,
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "current_price": 175.50,
        "prev_close": 174.20,
        "pct_change_since_close": 0.75,
        "cash_balance": 10500.25,
        "qty_owned": 15.0,
        "holding_value": 2632.50,

        "symbol_id": 42,
        "last_updated": "2026-06-17 14:30:00",
        "market_open": 174.50,
        "market_cap": 2730000000000,
        "eps": 6.13,
        "beta": 1.28,
        "trailing_pe": 28.63,
        "forward_pe": 26.12,
        "profit_margin": 0.258,
        "shares_outstanding": 15550000000,
        "book_value": 4.36,
        "price_to_book": 40.25,
        "dividend_yield": 0.0055,
        "fifty_two_week_high": 199.62,
        "fifty_two_week_low": 164.08,
        "fifty_day_average": 172.45,
        "two_hundred_day_average": 178.10,
        "rating": "Buy",
        "insider_sentiment": 0.65,
        "analyst_count": 38,
        "target_price": 195.00,
        "current_ratio": 1.04,
        "debt_to_equity": 1.45,
        "todays_volume": 52300000,
        "ten_day_avg_volume": 48500000,
        "three_month_avg_volume": 55000000
    };

    const pendingOrder = {
        'txTicker': 'AAPL',
        'txType': 'buy',
        'txShareQty': 10,
        'txDollarQty': 1750.00,
        'txUnit': 'shares'
    };
    // ^ DELETE ^ THESE ARE STUBS

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
        <form onSubmit={handleSubmitTradeOrder} className='card'>
            <h2>Confirm Your Transaction</h2>
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