import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { parseResponse } from '@/scripts/utils'
import SearchListItem from './SearchListItem';
import SearchListHeader from './SearchListHeader';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';


export default function SearchBar() {
    /*
    The search bar component for the header.

        Function: 
            - Requests to the internal OFFLINE search url, verifies response, and holds this state.
                'Offline' meaning searches internal db first, instead of external search api.
                Does this in order to show a "suggestions" datalist while user types.
            
            - Sorts list items in datalist.

            - Toggles visibility of data list.
    */

    let navigate = useNavigate();

    const [query, setQuery] = useState("");
    const [companyResults, setCompanyResults] = useState([]);
    const [userResults, setUserResults] = useState([]);
    const [newsResults, setNewsResults] = useState([]);
    const timeoutRef = useRef(null);

    const [dataListVisible, setDataListVisible] = useState(false);

    // Clears timer on dismount.
    useEffect(() => {
        return () => clearTimeout(timeoutRef.current);
    }, []);

    async function searchOffline() {
        // Hit 'local' routes that check DB first, prior to using online api.
        try {
            const [companies, users, news] = await Promise.all([
                fetch(`/api/search/companies?q=${encodeURIComponent(query)}&local=true`),
                fetch(`/api/search/users?q=${encodeURIComponent(query)}`),
                fetch(`/api/search/news?q=${encodeURIComponent(query)}&local=true`)
            ]);

            setCompanyResults((await parseResponse(companies))?.data || []);
            setUserResults((await parseResponse(users))?.data || []);
            setNewsResults((await parseResponse(news))?.data || [])
            setDataListVisible(true);

        } catch (error) {
            setDataListVisible(false);
            setCompanyResults([]);
            setUserResults([]);
            setNewsResults([]);
            console.error(error);
        }
    }

    async function handleKeyUp(event) {
        const query = String(event.target.closest('input').value).trim();
        setQuery(query);

        if (!query.length) {
            setDataListVisible(false);
            setCompanyResults([]);
            setUserResults([]);
            setNewsResults([]);
            return;
        }
        timeoutRef && clearTimeout(timeoutRef.current);
        timeoutRef.current = setTimeout(() => {
            searchOffline(query);
        }, 300)
    }

    function handleSubmit(event) {
        event.preventDefault();
        setDataListVisible(false);
        navigate(`/search?q=${encodeURIComponent(query)}`);
    }

    return (
        <form name='searchForm' onSubmit={handleSubmit}>
            <div className="relative z-20 flex items-center gap-2">
                <Input
                    id='searchBar'
                    type='text'
                    className="flex-1"
                    onKeyUp={handleKeyUp}
                    onBlur={() => setDataListVisible(false)}
                    onFocus={() => setDataListVisible(true)}
                    autoComplete="off"
                    placeholder="Search companies, users, news"
                />
                <Button disabled={!query} type='submit'>Search</Button>
                {
                    dataListVisible
                    &&
                    (companyResults.length > 0 || newsResults.length > 0 || userResults.length > 0)
                    &&
                    (<ul className="absolute top-full left-0 z-20 mt-1 max-h-96 w-full overflow-y-auto rounded-2xl bg-popover p-1 text-sm shadow-2xl ring-1 ring-foreground/10">
                        {companyResults.length > 0 && (
                            <div>
                                <SearchListHeader text={"Companies"} />
                                {companyResults.map((result) => (<SearchListItem key={result.ticker} object={result} type={'company'} />))}
                            </div>
                        )}

                        {userResults.length > 0 && (
                            <div>
                                <SearchListHeader text={"Users"} />
                                {userResults.map((result) => (<SearchListItem key={result.user_id} object={result} type={'user'} />))}
                            </div>
                        )}

                        {newsResults.length > 0 && (
                            <div>
                                <SearchListHeader text={"News"} />
                                {newsResults.map((result) => (<SearchListItem key={result.uuid} object={result} type={'news'} />))}
                            </div>
                        )}
                    </ul>)
                }
            </div>
        </form>
    );
}