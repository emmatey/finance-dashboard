import { useEffect, useState } from 'react';
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
                Insert headers for category boundaries. 
                This requires a registry of component ids.

            - Toggles visibility of data list.

    */

    const [componentRegistry, setComponentRegistry] = useState({
        'companies': [],
        'users': [],
        'news': []
    });

    async function searchOffline(query) {
        const safeQuery = String(query).trim();
        // Hit 'local' routes that check DB first, prior to using online api.

        const searchResponses = await Promise.all([
            fetch(`/api/search/companies?q=${safeQuery}&local=true`),
            fetch(`/api/search/users?q=${safeQuery}`),
            fetch(`/api/search/news?q=${safeQuery}&local=true`)
        ]);

        promises.map((promise) => (parseResponse(promise)));
    }

    async function handleKeyUp(event) {
        const query = event.target.value;
        if (!query.trim()) {
            setListIsOpen(false);
            setCompanyData([]);
            return;
        }
        setTimeout(async () => {
            try {
                const results = await searchOffline(query);
                setSearchResults(results);
            } catch (err) {
                console.error(err);
            };
        }, 200)
    }

    return (
        <div>
            <input id='searchBar' type='text' onKeyUp={handleKeyUp} />
            {
                componentRegistry.companies.length > 0
                ||
                componentRegistry.news.length > 0
                ||
                componentRegistry.users.length > 0
                &&
                (<ul>
                    {componentRegistry.companies.length > 0 && (
                        <SearchListHeader text={"Companies"}/>
                        componentRegistry.map((item) => (
                        <SearchListItem />))
                        )
                    }

                    {componentRegistry.users.length > 0 && <SearchListHeader text={"Users"}/>}

                    {componentRegistry.news.length > 0 && <SearchListHeader text={"News"}/>}
                </ul>)
            }
        </div>
    );
} 