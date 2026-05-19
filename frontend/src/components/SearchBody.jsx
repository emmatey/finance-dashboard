import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { searchOnline } from '../scripts/backend-fetch.js'

export default function SearchBody({ query }) {
    const [data, setData] = useState(null)
    const [error, setError] = useState(null)
    const navigate = useNavigate()

    useEffect(() => {
        async function fetchSearch(query_str=query) {
            const result = await searchOnline(query_str)
            if (result?.success) {
                setData(result);
            };
        }
        fetchSearch(query)
    }, [query])

    if (!query) return <main><h2>Search</h2><p>Enter a query to search.</p></main>
    if (error) return <main><h2>Search: {query}</h2><p>Error: {error}</p></main>
    if (!data) return <main><h2>Search: {query}</h2><p>Loading...</p></main>
   
    const companies = data?.companies ?? []
    const news = data?.news ?? []
    const users = data?.users ?? []

    return (
        <main>
            <h2>Search: {query}</h2>

            {companies.length > 0 && (
                <section>
                    <h3>Companies</h3>
                    <ul>
                        {companies.map((c, i) => (
                            <li key={i}>
                                <a
                                    href={`/research?ticker=${c?.ticker ?? ''}`}
                                    onClick={e => { e.preventDefault(); navigate(`/research?ticker=${c?.ticker ?? ''}`) }}
                                >
                                    {c?.ticker}: {c?.company_name} — {c?.exchange}
                                </a>
                            </li>
                        ))}
                    </ul>
                </section>
            )}

            {news.length > 0 && (
                <section>
                    <h3>News</h3>
                    <ul>
                        {news.map((n, i) => (
                            <li key={i}>
                                <a href={n?.link} target='_blank' rel='noreferrer'>{n?.title}</a>
                            </li>
                        ))}
                    </ul>
                </section>
            )}

            {users.length > 0 && (
                <section>
                    <h3>Users</h3>
                    <ul>
                        {users.map((u, i) => (
                            <li key={i}>
                                <a
                                    href={`/user/${u?.username ?? ''}`}
                                    onClick={e => { e.preventDefault(); navigate(`/user/${u?.username ?? ''}`) }}
                                >
                                    {u?.username} — Rank: {u?.rank ?? 'N/A'}
                                </a>
                            </li>
                        ))}
                    </ul>
                </section>
            )}

            {companies.length === 0 && news.length === 0 && users.length === 0 && (
                <p>No results found for "{query}".</p>
            )}
        </main>
    )
}
