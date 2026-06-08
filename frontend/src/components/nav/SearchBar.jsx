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

            - Toggles visibility of data list.

    */

    const [companyResults, setCompanyResults] = useState([]);
    const [userResults, setUserResults] = useState([]);
    const [newsResults, setNewsResults] = useState([]);

    async function searchOffline(query) {
        const safeQuery = String(query).trim();
        // Hit 'local' routes that check DB first, prior to using online api.
        try {
            const [companies, users, news] = await Promise.all([
                fetch(`/api/search/companies?q=${safeQuery}&local=true`),
                fetch(`/api/search/users?q=${safeQuery}`),
                fetch(`/api/search/news?q=${safeQuery}&local=true`)
            ]);
            setCompanyResults(parseResponse(companies).data);
            setUserResults (parseResponse(users).data);
            setNewsResults (parseResponse(news).data);

            console.log(companyResults);
            console.log(userResults);
            console.log(newsResults);

        } catch (error) {
            console.error(error);
        }
    }

    async function handleKeyUp(event) {
        const query = event.target.value;
        if (!query.length) {
            setCompanyResults([]);
            setUserResults([]);
            setNewsResults([]);
            return;
        }
        setTimeout(async () => {
            await searchOffline(query);
        }, 200)
    }

    return (
        <div>
            <input id='searchBar' type='text' onKeyUp={handleKeyUp} />
            {
                companyResults.length > 0
                ||
                newsResults.length > 0
                ||
                userResults.length > 0
                &&
                (<ul>
                    {companyResults.length > 0 && (
                        <div>
                            <SearchListHeader text={"Companies"} />
                            { companyResults.map((result) => (<SearchListItem object={result} type={company} />)) }
                        </div>
                    )}

                    {componentRegistry.users.length > 0 && <SearchListHeader text={"Users"} />}

                    {componentRegistry.news.length > 0 && <SearchListHeader text={"News"} />}
                </ul>)
            }
        </div>
    );
} 