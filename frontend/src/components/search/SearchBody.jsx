import { useState, useEffect } from 'react'
import { parseResponse } from '../../scripts/utils.js'
import '../../styles/utilities.css'

export default function SearchBody({ query }) {
    const [results, setResults] = useState(null);

    async function searchOnline(query) {
        const safeQuery = String(query).trim();
        try {
            const response = await fetch(`/api/search?q=${safeQuery}`);
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
                {(results.companies ?? []).map((c) => (
                    <li key={c.ticker}>{c.ticker}: {c.company_name} - {c.exchange}</li>
                ))}
                {(results.users ?? []).map((u) => (
                    <li key={u.user_id}>User: {u.username} - Rank: {u.rank ?? 'N/A'}</li>
                ))}
                {(results.news ?? []).map((n) => (
                    <li key={n.uuid}>News: {n.title} ({n.publisher})</li>
                ))}
            </ul>
        </div>
    );
}
