import { useState, useEffect } from 'react'
import { parseResponse } from '../../../scripts/utils.js'
import TradeSearch from './TradeSearch.jsx'
import TradeOrderForm from './TradeOrderForm.jsx'
import '../../../styles/utilities.css'
import '../../../styles/colors.css'

// Assembles the trade shard from two children that share the same backend
// result: TradeSearch (search bar + results panel) drives `activeQuery`, and
// the polling fetch below produces `tickerInfoJson`. Both pieces are owned
// here so TradeOrderForm can read the active ticker/result as well.
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
                    break;
                default:
                    const tickerJson = await parseResponse(tickerInfoResponse) || {};
                    setTickerInfoJson(tickerJson);
                    setLoading(false);
            };
        } catch (error) {
            setLoading(false);
            setTickerInfoJson({ "error": `${error}` });
            console.error(error);
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
            await getTickerInfoFromTradeRoute(activeQuery);
            timerId = setTimeout(() => {
                tick();
            }, 60000)
        }

        tick();

        return () => { clearTimeout(timerId) }
    }, [activeQuery]);

    return (
        <div className='card'>
            <TradeSearch
                activeQuery={activeQuery}
                setActiveQuery={setActiveQuery}
                loading={loading}
                tickerInfoJson={tickerInfoJson}
            />
            <TradeOrderForm
                activeQuery={activeQuery}
                tickerInfoJson={tickerInfoJson}
            />
        </div>
    )
}
