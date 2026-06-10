import { useState, useEffect } from 'react'
import { parseResponse } from '../../scripts/utils.js'
import SearchListItem from './SearchListItem'
import SearchListHeader from './SearchListHeader'
import '../../styles/utilities.css'

export default function SearchBody({ query }) {
    const [results, setResults] = useState(null);

    async function searchOnline(query) {
        const safeQuery = String(query).trim();
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(safeQuery)}`);
            return await parseResponse(response);
        } catch (error) {
            setResults([]);
            console.error(error);
        }
    }

    useEffect(() => {
        if (!query) return;
        searchOnline(query).then(setResults);
    }, [query]);

    if (!query) return <p>No query provided.</p>;
    if (!results) return <p>Loading...</p>;

    return (
        <div className='card'>
            <ul>
                {(results.companies ?? []).length > 0 && (
                    <div>
                        <SearchListHeader text={"Companies"} />
                        {results.companies.map((object) => (
                            <SearchListItem key={object.ticker} object={object} type='company' />
                        ))}
                    </div>
                )}
                {(results.users ?? []).length > 0 && (
                    <div>
                        <SearchListHeader text={"Users"} />
                        {results.users.map((object) => (
                            <SearchListItem key={object.user_id} object={object} type='user' />
                        ))}
                    </div>
                )}
                {(results.news ?? []).length > 0 && (
                    <div>
                        <SearchListHeader text={"News"} />
                        {results.news.map((object) => (
                            <SearchListItem key={object.uuid} object={object} type='news' />
                        ))}
                    </div>
                )}
            </ul>
        </div>
    );
}