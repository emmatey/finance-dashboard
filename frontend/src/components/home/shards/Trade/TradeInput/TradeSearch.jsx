import { useRef, useState } from 'react'
import { parseResponse } from '@/scripts/utils.js'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'


export default function TradeSearch({ activeQuery, setActiveQuery, loading }) {
    const [pendingQuery, setPendingQuery] = useState("");
    const [dataList, setDataList] = useState([]); // [[company_name, ticker], ...]
    const [dataListVisible, setDataListVisible] = useState(false);
    const [resolving, setResolving] = useState(false);
    const debounceRef = useRef(null);

    async function getDataListItemsFromSearchRoute(query) {
        // Make a GET request to the '/api/search/companies' route in order to populate the datalist.
        // Stays on the local/offline route - this fires on every keystroke, so it can't afford
        // a live Yahoo Finance hit each time.
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

    async function resolveTickerOnline(query) {
        // Search button submits go through the live/online route (no local=true) so a typed
        // company name (not just a ticker) can resolve to a real ticker, even one not yet
        // cached locally.
        try {
            const res = await fetch(`/api/search/companies?q=${encodeURIComponent(query)}&limit=1`);
            const data = await parseResponse(res);
            return data?.data?.[0]?.ticker ?? null;
        } catch (error) {
            console.error(error);
            return null;
        }
    }

    async function runOnlineSearch(rawQuery) {
        const query = rawQuery.trim();
        if (!query) return;

        setDataListVisible(false);
        setPendingQuery("");
        setResolving(true);
        const resolvedTicker = await resolveTickerOnline(query);
        setResolving(false);
        setActiveQuery(resolvedTicker ?? query);
    }

    function handleSearchSubmit(event) {
        event.preventDefault();
        runOnlineSearch(pendingQuery);
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
                    {dataListVisible && pendingQuery.trim() && (
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
                            <li className={dataList.length > 0 ? "mt-1 border-t border-border pt-1" : ""}>
                                <button
                                    type="button"
                                    className="w-full rounded-xl px-3 py-2 text-left text-muted-foreground hover:bg-muted hover:text-foreground"
                                    onMouseDown={() => runOnlineSearch(pendingQuery)}
                                >
                                    Not seeing what you're looking for? Hit search to run a deep search.
                                </button>
                            </li>
                        </ul>
                    )}
                </div>
                <Button type='submit' disabled={resolving}>{resolving ? 'Searching...' : 'Search'}</Button>
            </div>
        </form>
    )
}
