import { useRef, useState } from 'react'
import { parseResponse } from '@/scripts/utils.js'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'


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

    function handleSuggestionSelect(query) {
        setDataListVisible(false);
        setActiveQuery(query);
        setPendingQuery("");
    }

    return (
        <form name='tradeSearchForm' onSubmit={handleSearchSubmit}>
            <div className="flex items-center gap-2">
                <div className="relative z-20 flex-1">
                    <Input
                        name='searchInput'
                        type='text'
                        value={pendingQuery}
                        onChange={handleSearchChange}
                        onClick={pendingQuery ? () => setDataListVisible(true) : () => setDataListVisible(false)}
                        onBlur={() => setDataListVisible(false)}
                        autoComplete="off"
                        placeholder="Search for a ticker or company"
                    />
                    {dataList.length > 0 && dataListVisible && (
                        <ul className="absolute top-full left-0 z-20 mt-1 max-h-64 w-full overflow-y-auto rounded-2xl bg-popover p-1 text-sm shadow-2xl ring-1 ring-foreground/10">
                            {dataList.map((arr) => (
                                <li key={arr[1]}>
                                    <button
                                        type="button"
                                        className="w-full rounded-xl px-3 py-2 text-left hover:bg-muted"
                                        onMouseDown={() => handleSuggestionSelect(arr[1])}
                                    >
                                        {`${arr[1] === "null" ? null : arr[1]} - ${arr[0] === "null" ? null : arr[0]}`}
                                    </button>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
                <Button type='submit'>Search</Button>
            </div>
        </form>
    )
}
