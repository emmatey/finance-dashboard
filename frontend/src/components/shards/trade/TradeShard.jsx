import { useState, useEffect, useRef } from 'react'
import { parseResponse } from '../../../scripts/utils.js'
import '../../../styles/utilities.css'
import '../../../styles/colors.css'

export default function TradeShard( {queryProp} ) {
    const [query, setQuery] = useState(queryProp || "");
    const [loading, setLoading] = useState(false);
    const [tickerInfoJson, setTickerInfoJson] = useState(null);
    const timeoutRef = useRef(null);
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

    function getTrade() {
        // Makes a GET request to the '/api/trade' route.
        try {
            const tickerInfoResponse = await fetch(`/api/trade?ticker=${query}`);
            const tickerInfoJson = setTickerInfoJson((await parseResponse(tickerInfoResponse)?.data || []));
        } catch (error) {
            setLoading(false);
            setTickerInfoJson([]);
            console.error(error);
        }
    }

    function postTrade() {
        // Makes a POST request to the '/api/trade' route.

    }

    function handleSearchSubmit() {

    }

    function handleTransactSubmit() {
        
    }

    // Refreshes price data on a timer.
    useEffect(() => {
        if (!query) {

        }
        return(<></>)
    }, [query])

    // Clears timer on dismount.
    useEffect(() => {
        return (() => clearTimeout(timeoutRef.current));
    }, []);

    return (
        <div className='card'>
            <form name='tradeSearchForm' onSubmit={handleSearchSubmit} >
                <input type='text'/>
                <button type='submit'> Search </button>
        
            </form>
        </div>
    )
}