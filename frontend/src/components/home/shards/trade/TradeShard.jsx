import { useState, useEffect } from 'react'
import { parseResponse, adjustPendingOrder } from '../../../../scripts/utils.js'
import TradeInput from './TradeInput.jsx'
import TradeOrderConfirm from './TradeOrderConfirm.jsx'
import TradePostOrderSummary from './TradePostOrderSummary.jsx'
import '../../../../styles/utilities.css'
import '../../../../styles/colors.css'

export default function TradeShard() {
    const [activeQuery, setActiveQuery] = useState("");
    const [loading, setLoading] = useState(false);

    const [tickerInfoJson, setTickerInfoJson] = useState(null);
    
    let currentPrice = null;
    let ticker = null;
    if (tickerInfoJson) {
        currentPrice = tickerInfoJson.current_price;
        ticker = tickerInfoJson.ticker;
    }

    const [pendingOrder, setPendingOrder] = useState({
        'txTicker': null,
        'txType': null,
        'txShareQty': null,
        'txDollarQty': null,
        'txUnit': null
    });

    const [showInputScreen, setShowInputScreen] = useState(true);
    const [showConfirmationScreen, setShowConfirmationScreen] = useState(false);
    const [showSummaryScreen, setShowSummaryScreen] = useState(false);

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
    }, [activeQuery, showConfirmationScreen]);

    useEffect(() => {
        if (!tickerInfoJson || !tickerInfoJson.current_price) {
            return;
        }

        const { current_price: freshPrice, ticker: freshTicker } = tickerInfoJson;

        setPendingOrder((prevOrder) => {
            if (!prevOrder.txUnit) {
                return prevOrder;
            }

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
                />
            )}
        </div>
    );
}