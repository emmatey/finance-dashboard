import { useState, useEffect } from 'react'
import { parseResponse } from '../../../../scripts/utils.js'
import TradeSearch from './TradeSearch.jsx'
import TradeOrderForm from './TradeOrderForm.jsx'
import '../../../../styles/utilities.css'
import '../../../../styles/colors.css'


export default function TradeShard({ queryProp }) {
    const safeQueryProp = String(queryProp ?? "").trim();
    const [activeQuery, setActiveQuery] = useState(safeQueryProp || "");
    const [loading, setLoading] = useState(false);
    const [tickerInfoJson, setTickerInfoJson] = useState(null);

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
            // Only reschedule the next poll when the fetch succeeds. A 404
            // (ticker not found) or any error returns false, which stops the
            // loop so we don't keep polling a missing/broken ticker.
            const ok = await getTickerInfoFromTradeRoute(activeQuery);
            if (ok) {
                timerId = setTimeout(() => {
                    tick();
                }, 60000)
            }
        }

        tick();

        return () => { clearTimeout(timerId) }
    }, [activeQuery]);

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
                />
            </div>
        </div >
    )
}
