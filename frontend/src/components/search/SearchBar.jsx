import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { parseResponse } from '../../scripts/utils'
import SearchListItem from './SearchListItem';
import SearchListHeader from './SearchListHeader';


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

    const [companyResults, setCompanyResults] = useState([]);
    const [userResults, setUserResults] = useState([]);
    const [newsResults, setNewsResults] = useState([]);
    const [dataListVisible, setDataListVisible] = useState(false);
    const timeoutRef = useRef(null);

    // Clears timer on dismount.
    useEffect(() => {
        return () => clearTimeout(timeoutRef.current);
    }, []);

    async function searchOffline(query) {
        const safeQuery = String(query).trim();
        // Hit 'local' routes that check DB first, prior to using online api.
        try {
            const [companies, users, news] = await Promise.all([
                fetch(`/api/search/companies?q=${safeQuery}&local=true`),
                fetch(`/api/search/users?q=${safeQuery}`),
                fetch(`/api/search/news?q=${safeQuery}&local=true`)
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
        const query = event.target.value;
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

    return (
        <div style={{ position: 'relative' }}>
            <input
                id='searchBar'
                type='text'
                onKeyUp={handleKeyUp}
                onBlur={() => setDataListVisible(false)}
                onFocus={() => setDataListVisible(true)}
            />
            {
                dataListVisible
                &&
                (companyResults.length > 0 || newsResults.length > 0 || userResults.length > 0)
                &&
                (<ul>
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
    );
} 