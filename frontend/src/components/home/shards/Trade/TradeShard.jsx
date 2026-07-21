import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { adjustPendingOrder } from '@/scripts/utils.js'
import useTickerInfo from './useTickerInfo.js'
import TradeInput from './TradeInput.jsx'
import TradeOrderConfirm from './TradeOrderConfirm.jsx'
import TradePostOrderSummary from './TradePostOrderSummary.jsx'


export default function TradeShard() {
    const [searchParams] = useSearchParams();
    const [activeQuery, setActiveQuery] = useState(searchParams.get('ticker')?.toUpperCase() ?? "");
    const { tickerInfoJson, loading } = useTickerInfo(activeQuery);
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
        <div className="mx-auto max-w-5xl">
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