import { useState, useEffect, useRef } from 'react'
import { parseResponse } from '../../../scripts/utils.js'
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

    // Updates data about current company every 60 seconds.
    //useEffect(() => {
    //   let timerId = null; 
    //
    //   async function tick() {
    //        await getTrade();
    //        timerId = setTimeout(() => {
    //            tick();
    //        }, 60000)
    //   }
    //
    //   tick();
    //
    //   return () => {clearTimeout(timerId)}
    //}, [currentQuery]);

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
                                        key={arr[1]}
                                        className='card'
                                        onMouseDown={() => handleSuggestionSelect(arr[1])}
                                    >
                                        {`${arr[1]} - ${arr[0]}`}
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