import { useState } from 'react'
import { parseResponse } from '../../../scripts/utils.js'
import { getRandomIntInclusive } from '../../../scripts/utils.js'
import '../../../styles/utilities.css'
import '../../../styles/colors.css'

// Search bar with autocomplete suggestions plus the results panel that
// displays info about the active ticker. The active query and its backend
// result are owned by the parent shard so the order form can read them too.
export default function TradeSearch({ activeQuery, setActiveQuery, loading, tickerInfoJson }) {
    const [pendingQuery, setPendingQuery] = useState("");
    const [dataList, setDataList] = useState([]);
    const [dataListVisible, setDataListVisible] = useState(false);

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

    // https://developer.mozilla.org/en-US/docs/Web/API/FocusEvent/relatedTarget
    return (
        <>
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
        </>
    )
}
