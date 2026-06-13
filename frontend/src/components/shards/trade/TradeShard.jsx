import { useState, useEffect, useRef } from 'react'
import { parseResponse } from '../../../scripts/utils.js'
import { getRandomIntInclusive } from '../../../scripts/utils.js'
import '../../../styles/utilities.css'
import '../../../styles/colors.css'

export default function TradeShard({ queryProp }) {
    const safeQueryProp = String(queryProp ?? "").trim();
    const [currentQuery, setCurrentQuery] = useState(safeQueryProp);
    const [loading, setLoading] = useState(false);
    const [tickerInfoJson, setTickerInfoJson] = useState(null);
    const [dataList, setDataList] = useState([]);
    const [dataListVisible, setDataListVisible] = useState(false);


    async function getTrade() {
        // Makes a GET request to the '/api/trade' route.
        if (!currentQuery) {
            console.warn("no query provided on getTrade call.")
            return
        };

        try {
            setLoading(true);
            const tickerInfoResponse = await fetch(`/api/trade?ticker=${encodeURIComponent(currentQuery)}`);
            const tickerJson = await parseResponse(tickerInfoResponse) || {}
            setTickerInfoJson(tickerJson);
            setLoading(false);
        } catch (error) {
            setLoading(false);
            setTickerInfoJson({});
            console.error(error);
        }
    }

    async function getSearch(query) {
        // Make a GET request to the '/api/search' route.
        try {
            const companies = await fetch(`/api/search/companies?q=${encodeURIComponent(query)}`);
            const res = await parseResponse(companies);
            const data = res?.data || [];
            setDataList(data.map((obj) => ([obj.company_name, obj.ticker])));
        } catch (error) {
            setDataList([]);
            console.error(error);
        }
    }

    function postTrade() {
        // Makes a POST request to the '/api/trade' route.

    }

    async function handleSearchSubmit(event) {
        event.preventDefault();
        getSearch();
    }

    function handleSearchChange(event) {
        const query = String(event.target.value).trim();
        setCurrentQuery(query);
        getSearch(query);
        setDataListVisible(true);
    }

    function handleSuggestionSelect(ticker) {
        setCurrentQuery(ticker);
        setDataListVisible(false);
    }

    function handleTransactSubmit(event) {
        event.preventDefault();
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

    // Updates data about current company every 60 seconds.
    useEffect(() => {
       let timerId = null; 
    
       async function tick() {
            await getTrade();
            timerId = setTimeout(() => {
                tick();
            }, 60000)
       }
    
       tick();
    
       return () => {clearTimeout(timerId)}
    }, [currentQuery]);

    return (
        <div className='card'>
            <form name='tradeSearchForm' onSubmit={handleSearchSubmit} >
                <div>
                    <div style={{ position: 'relative', display: 'inline-block' }}>
                        <input
                            name='searchInput'
                            type='text'
                            value={currentQuery}
                            onChange={handleSearchChange}
                            onClick={() => setDataListVisible(true)}
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
                loading ? <h4> Loading... </h4> :
                    <ul>
                        {
                            !tickerInfoJson
                                ?
                                <li>No info found...</li>
                                :
                                Object.entries(tickerInfoJson).map(([k, v]) => (
                                    <li key={k}>{k}: {String(v)}</li>
                                ))
                        }
                    </ul>
            }

            <form name='tradeTransactForm' onSubmit={handleTransactSubmit}>
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