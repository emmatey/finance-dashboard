import { useRef, useState } from 'react'
import { parseResponse, getRandomAccentColor } from '@/scripts/utils.js'
import '@/styles/utilities.css'
import '@/styles/colors.css'


export default function TradeSearch({ activeQuery, setActiveQuery, loading }) {
    const [pendingQuery, setPendingQuery] = useState("");
    const [dataList, setDataList] = useState([]); // [[company_name, ticker], ...]
    const [dataListVisible, setDataListVisible] = useState(false);
    const debounceRef = useRef(null);

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
        setPendingQuery("");
    }

    function handleSearchChange(event) {
        const query = String(event.target.value).trim();
        setPendingQuery(query);

        debounceRef && clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => {
            getDataListItemsFromSearchRoute(query);
            setDataListVisible(true);
        }, 300)
    }

    function handleSuggestionMouseOver(event) {
        event.target.style.background = getRandomAccentColor();
    }

    function handleSuggestionMouseLeave(event) {
        const el = event.target;
        el.style.background = 'var(--color-surface)';
    }

    function handleSuggestionSelect(query) {
        setDataListVisible(false);
        setActiveQuery(query);
        setPendingQuery("");
    }

    return (
        <>
            <form name='tradeSearchForm' onSubmit={handleSearchSubmit} >
                <div>
                    <div style={{ position: 'relative', display: 'inline-block', zIndex: 2}}>
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
        </>
    )
}
