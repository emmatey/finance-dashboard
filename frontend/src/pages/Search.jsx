import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { unpackFetchResponse } from '../scripts/utils.js'
import Header from '../components/Header.jsx'
import Footer from '../components/Footer.jsx'

async function searchOnline(query) {
    const safeQuery = String(query).trim();
    const response = await fetch(`/api/search?q=${safeQuery}`);
    const data = await unpackFetchResponse(response);
    return data;
}

function SearchBody({ query }) {
    const [results, setResults] = useState(null);

    useEffect(() => {
        if (!query) return;
        searchOnline(query).then(setResults);
    }, [query]);

    if (!query) return <p>No query provided.</p>;
    if (!results) return <p>Loading...</p>;

    return (
        <div>
            <ul>
                {(results.companies ?? []).map((c, i) => (
                    <li key={i}>{c.ticker}: {c.company_name} - {c.exchange}</li>
                ))}
                {(results.users ?? []).map((u, i) => (
                    <li key={i}>User: {u.username} - Rank: {u.rank ?? 'N/A'}</li>
                ))}
                {(results.news ?? []).map((n, i) => (
                    <li key={i}>News: {n.title} ({n.publisher})</li>
                ))}
            </ul>
        </div>
    );
}

export default function Search() {
    const [searchParams] = useSearchParams()
    const query = searchParams.get('q')

    return (
        <>
            <Header />
            <SearchBody query={query} />
            <Footer />
        </>
    )
}
