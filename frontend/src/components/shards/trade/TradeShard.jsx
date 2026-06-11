import { useState, useEffect, useRef } from 'react'
import { parseResponse } from '../../../scripts/utils.js'
import '../../../styles/utilities.css'
import '../../../styles/colors.css'

export default function TradeShard({ queryProp }) {
    const safeQueryProp = String(queryProp ?? "").trim();
    const [loading, setLoading] = useState(false);
    const [tickerInfoJson, setTickerInfoJson] = useState(null);
    // GET Returns data to populate the order preview screen.
    // POST Executes a buy or sell transaction.

    // Preview
    // 1. request to trade url to get data on selected ticker
    // Ticker will come in from two places, as a prop, or as a value of an internal el
    // check for prop first, if not check input element next.
    // 2. Start a timer on the age of the data. 60s?
    // 2a. If the data gets older than that, refresh it. The state shown to the user will be
    // the price of the order in the ledger. 

    // Transact
    // 1. Callback
    async function runTask(func, param, interval) {
        let isRunning = true;
        // edit this to use a useEffect with a dependency on the query that calls the cleanup callback on return
        // or use a use ref to store the callback which stops the loop
        async function run() {
            if (isRunning) {
                await func(param);
                setTimeout(() => (
                    run()
                ), interval)
            }
        }

        run();

        return () => (isRunning = false)
    }

    async function getTrade(query) {
        // Makes a GET request to the '/api/trade' route.
        try {
            setLoading(true);
            const tickerInfoResponse = await fetch(`/api/trade?ticker=${query}`);
            const tickerJson = await parseResponse(tickerInfoResponse) || {}
            setTickerInfoJson(tickerJson);
            setLoading(false);
        } catch (error) {
            setLoading(false);
            setTickerInfoJson({});
            console.error(error);
        }
    }

    function postTrade() {
        // Makes a POST request to the '/api/trade' route.

    }

    async function handleSearchSubmit(event) {
        event.preventDefault();
        // change this to query the event.queryselector
        const query = String(document.getElementsByName('searchInput')[0].value).trim();
        return runTask(getTrade, query, 60000);
    }

    function handleTransactSubmit(event) {
        event.preventDefault();
    }
    
    return (
        <div className='card'>
            <form name='tradeSearchForm' onSubmit={handleSearchSubmit} >
                <input name='searchInput' type='text' />
                <button type='submit'> Search </button>
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