import { useState, useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'

export default function usePortfolio() {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [responseCode, setResponseCode] = useState(null);

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const res = await fetch('/api/user/portfolio');
                const data = await parseResponse(res);
                setData(data?.data ?? []);
            } catch (err) {
                console.error(err);
                setResponseCode(err.status ?? null);
                if (err.status === 400) {
                    setError(`Error: ${responseCode} No user session found. Please log in.`);
                } else if (err.status === 404) {
                    setError(`Error: ${responseCode} User not found.`);
                } else if (err.status === 500) {
                    setError(`Error: ${responseCode} Could not load portfolio. Please try again later.`);
                } else {
                    setError(`Error: ${responseCode} An unexpected error occurred. Please try again.`);
                }
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [])

    return { loading, data, error };
}
