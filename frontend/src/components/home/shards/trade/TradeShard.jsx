import { useState, useEffect, useSyncExternalStore } from 'react'
import { parseResponse, adjustPendingOrder } from '../../../../scripts/utils.js'
import TradeSearch from './TradeSearch.jsx'
import TradeOrderForm from './TradeOrderForm.jsx'
import '../../../../styles/utilities.css'
import '../../../../styles/colors.css'


export default function TradeShard() {
    const [activeQuery, setActiveQuery] = useState("");
    const [loading, setLoading] = useState(false);

    const [tickerInfoJson, setTickerInfoJson] = useState(null);
    const [pendingOrder, setPendingOrder] = useState({
        'txType': null,
        'txShareQty': null,
        'txDollarQty': null,
        'txUnit': null
    });

    const [showInputScreen, setShowInputScreen] = useState(true);
    const [showConfirmationScreen, setShowConfirmationScreen] = useState(false);
    const [showSummaryScreen, setShowSummaryScreen] = useState(false);

    async function getTickerInfoFromTradeRoute(query) {
        // Makes a GET request to the '/api/trade' route.
        try {
            setLoading(true);
            const tickerInfoResponse = await fetch(`/api/trade?ticker=${encodeURIComponent(query)}`);
            switch (tickerInfoResponse.status) {
                case 404:
                    console.log(`Ticker ${query} not found.`);
                    setTickerInfoJson(null);
                    setLoading(false);
                    setIsInvalidTicker(true);
                    // Keep activeQuery set so "No info found..." renders.
                    return false;
                default:
                    const tickerJson = await parseResponse(tickerInfoResponse) || {};
                    setTickerInfoJson(tickerJson);
                    setLoading(false);
                    return true;
            };
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
        };

        let timerId = null;
        async function tick() {
            // getinfo...() returns bool
            const ok = await getTickerInfoFromTradeRoute(activeQuery);
            if (ok) {
                timerId = setTimeout(() => {
                    tick();
                }, 60000)
            }
        }

        tick();

        return () => { clearTimeout(timerId) }
    }, [activeQuery, showConfirmationScreen]);

    useEffect(() => {
        if (!tickerInfoJson || !tickerInfoJson.current_price) {
            return;
        }

        setPendingOrder((prevOrder) => {
            if (!prevOrder.txUnit) {
                return prevOrder;
            };

            const { txType, txShareQty, txDollarQty, txUnit } = prevOrder;
            const currentQty = txUnit === 'dollars' ? txDollarQty : txShareQty;
            const [newDollars, newShares] = adjustPendingOrder(
                txUnit,
                currentQty,
                tickerInfoJson.current_price
            );

            return {
                txType: txType,
                txUnit: txUnit,
                txShareQty: newShares,
                txDollarQty: newDollars,
            };
        });

    }, [tickerInfoJson]);

    return (
        <div style={{ display: 'flex' }}>
            <div className='card'>
                <TradeSearch
                    activeQuery={activeQuery}
                    setActiveQuery={setActiveQuery}
                    loading={loading}
                    tickerInfoJson={tickerInfoJson}
                />
            </div>
            <div className='card'>
                <TradeOrderForm
                    tickerInfoJson={tickerInfoJson}
                    setPendingOrder={setPendingOrder}
                />
            </div>
        </div >
    )
}
