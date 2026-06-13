import { useState, useEffect, useRef } from 'react'
import { parseResponse } from '../../../scripts/utils.js'
import { getRandomIntInclusive } from '../../../scripts/utils.js'
import '../../../styles/utilities.css'
import '../../../styles/colors.css'

export default function TradeShard({ queryProp }) {
    const safeQueryProp = String(queryProp ?? "").trim();
    const timeoutRef = useRef(null);
    const [pendingQuery, setPendingQuery] = useState("");
    const [activeQuery, setActiveQuery] = useState(safeQueryProp || "");
    const [loading, setLoading] = useState(false);
    const [tickerInfoJson, setTickerInfoJson] = useState(null);
    const [dataList, setDataList] = useState([]);
    const [dataListVisible, setDataListVisible] = useState(false);


    async function getTickerInfoFromTradeRoute(query) {
        // Makes a GET request to the '/api/trade' route.
        try {
            setLoading(true);
            const tickerInfoResponse = await fetch(`/api/trade?ticker=${encodeURIComponent(query)}`);
            switch (tickerInfoResponse.status) {
                case 404:
                    console.log(`Ticker ${activeQuery} not found.`);
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

    async function getDataListItemsFromSearchRoute(query) {
        // Make a GET request to the '/api/search/companies' route in order to populate the datalist.
        try {
            const companies = await fetch(`/api/search/companies?q=${encodeURIComponent(query)}&local=true`);
            const res = await parseResponse(companies);
            const data = res?.data || [];
            setDataList(data.map((obj) => ([obj.company_name, obj.ticker])));
        } catch (error) {
            setDataList([]);
            console.error(error);
        }
    }

    async function handleSearchSubmit(event) {
        event.preventDefault();
        setActiveQuery(pendingQuery);
    }

    function handleSearchChange(event) {
        const query = String(event.target.value).trim();
        setPendingQuery(query);
        getDataListItemsFromSearchRoute(query);
        setDataListVisible(true);
    }

    function handleSuggestionMouseOver(event) {
        const el = event.target;
        const val = getRandomIntInclusive(1, 4);
        if (val === 1) {
            el.style.background = 'var(--blue-3)';
        } else if (val === 2) {
            el.style.background = 'var(--yellow-4)';
        } else if (val === 3) {
            el.style.background = 'var(--red-3)';
        } else if (val === 4) {
            el.style.background = 'var(--green-3)';
        } else {
            throw new Error("invalid 'val' var in header.jsx");
        };
    }

    function handleSuggestionMouseLeave(event) {
        const el = event.target;
        el.style.background = 'var(--color-surface)';
    }

    function handleSuggestionSelect(query) {
        setDataListVisible(false);
        setActiveQuery(query);
        setPendingQuery(query);
    }

    function handleSubmitTradeOrder() {
        // Makes a POST request to the '/api/trade' route.

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
    // https://developer.mozilla.org/en-US/docs/Web/API/FocusEvent/relatedTarget
    return (
        <div className='card'>
            <form name='tradeSearchForm' onSubmit={handleSearchSubmit} >
                <div>
                    <div style={{ position: 'relative', display: 'inline-block' }}>
                        <input
                            name='searchInput'
                            type='text'
                            value={pendingQuery}
                            onChange={handleSearchChange}
                            onClick={pendingQuery ? () => setDataListVisible(true) : () => setDataListVisible(false)}
                            onBlur={() => setDataListVisible(false)}
                            autoComplete="off"
                        />
                        {dataList.length > 0 && dataListVisible &&
                            <ul style={{ position: 'absolute', top: '100%', left: 0, width: '100%', padding: 0, margin: 0 }}>
                                {dataList.map((arr) => (
                                    <li
                                        // arr = [name, ticker]
                                        key={arr[1]}
                                        className='card'
                                        onMouseDown={() => handleSuggestionSelect(arr[1])}
                                        onMouseOver={handleSuggestionMouseOver}
                                        onMouseLeave={handleSuggestionMouseLeave}
                                    >
                                        {`${arr[1] === "null" ? null : arr[1]} - ${arr[0] === "null" ? null : arr[0]}`}
                                    </li>
                                ))}
                            </ul>
                        }
                    </div>
                    <button type='submit'> Search </button>
                </div>
            </form>

            {
                loading ?
                    (<h4> Loading... </h4>)
                    :
                    !activeQuery ?
                        (null)
                        :
                        !tickerInfoJson ?
                            <ul>
                                <li>No info found...</li>
                            </ul>
                            :
                            <ul>
                                {Object.entries(tickerInfoJson).map(
                                    ([k, v]) => (
                                        <li
                                            key={k}>{k}: {String(v)}
                                        </li>
                                    ))}
                            </ul>
            }

            <form name='tradeTransactForm' onSubmit={handleSubmitTradeOrder}>
                <select name='txType'>
                    <option value='buy'>Buy</option>
                    <option value='sell'>Sell</option>
                </select>
                <div>
                    <input type='number' name='qtyInput' placeholder='Qty' min='0.1' step='0.1' />
                    <select name='qtyUnit'>
                        <option value='shares'>Shares</option>
                        <option value='dollars'>Dollars</option>
                    </select>
                </div>
                <button type='submit'>Submit</button>
            </form>
        </div>
    )
}