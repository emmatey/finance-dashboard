import { useState, useEffect } from 'react'
import { parseResponse, adjustPendingOrder } from '../../../../scripts/utils.js'
import TradeInput from './TradeInput.jsx'
import TradeOrderConfirm from './TradeOrderConfirm.jsx'
import TradePostOrderSummary from './TradePostOrderSummary.jsx'
import '../../../../styles/utilities.css'
import '../../../../styles/colors.css'

/*
    TODO: Add data about current users'existing holdings with the company.
        Use this info to check if the user is able to make a sell order.

        Catch errors with buying and selling. i.e. not enough shares to sell. 
            or not enough money to buy!
 */

export default function TradeShard() {
    const [activeQuery, setActiveQuery] = useState("");
    const [loading, setLoading] = useState(false);

    const [tickerInfoJson, setTickerInfoJson] = useState(null);
    let currentPrice = null;
    let ticker = null;

    const [pendingOrder, setPendingOrder] = useState({
        'txTicker': null,
        'txType': null,
        'txShareQty': null,
        'txDollarQty': null,
        'txUnit': null
    });
    const [orderSummaryData, setOrderSummaryData] = useState(null);

    const [showInputScreen, setShowInputScreen] = useState(true);
    const [showConfirmationScreen, setShowConfirmationScreen] = useState(false);
    const [showSummaryScreen, setShowSummaryScreen] = useState(false);
    const viewController = {
        'setShowInput': setShowInputScreen,
        'setShowConfirmationScreen': setShowConfirmationScreen,
        'setShowSummaryScreen': setShowSummaryScreen
    };

    async function getTickerInfoFromTradeRoute(query) {
        try {
            setLoading(true);
            const tickerInfoResponse = await fetch(`/api/trade?ticker=${encodeURIComponent(query)}`);
            switch (tickerInfoResponse.status) {
                case 404:
                    console.log(`Ticker ${query} not found.`);
                    setTickerInfoJson(null);
                    setLoading(false);
                    return false;
                default:
                    const tickerJson = await parseResponse(tickerInfoResponse) || {};
                    setTickerInfoJson(tickerJson);
                    setLoading(false);
                    return true;
            }
        } catch (error) {
            setLoading(false);
            setTickerInfoJson({ "error": `${error}` });
            console.error(error);
            return false;
        }
    }

    // Updates data about current company every 60 seconds.
    useEffect(() => {
        if (!activeQuery) {
            setTickerInfoJson(null);
            setLoading(false);
            return;
        }

        let timerId = null;
        async function tick() {
            const ok = await getTickerInfoFromTradeRoute(activeQuery);
            if (ok) {
                timerId = setTimeout(() => {
                    tick();
                }, 60000);
            }
        }

        tick();

        return () => { clearTimeout(timerId); };
    }, [activeQuery]);

    useEffect(() => {
        if (!tickerInfoJson || !tickerInfoJson.current_price || !pendingOrder['txTicker']) {
            return;
        }

        const { current_price: freshPrice, ticker: freshTicker } = tickerInfoJson;

        setPendingOrder((prevOrder) => {
            const { txType, txShareQty, txDollarQty, txUnit } = prevOrder;
            const currentQty = (txUnit === 'dollars' ? txDollarQty : txShareQty);
            const [newDollars, newShares] = adjustPendingOrder(txUnit, currentQty, freshPrice);

            return {
                txTicker: freshTicker,
                txType: txType,
                txUnit: txUnit,
                txShareQty: newShares,
                txDollarQty: newDollars,
            };
        });

    }, [tickerInfoJson]);

    return (
        <div className="card">
            {showInputScreen && (
                <TradeInput
                    activeQuery={activeQuery}
                    setActiveQuery={setActiveQuery}
                    loading={loading}
                    tickerInfoJson={tickerInfoJson}
                    setPendingOrder={setPendingOrder}
                    viewController={viewController}
                />
            )}

            {showConfirmationScreen && (
                <TradeOrderConfirm
                    pendingOrder={pendingOrder}
                    tickerInfoJson={tickerInfoJson}
                    setActiveQuery={setActiveQuery}
                    setOrderSummaryData={setOrderSummaryData}
                    viewController={viewController}
                />
            )}

            {showSummaryScreen && (
                <TradePostOrderSummary
                    orderSummaryData={orderSummaryData}
                    viewController={viewController}
                />
            )}
        </div>
    );
}