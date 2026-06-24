import { useState, useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'

export default function useTransactionHistory() {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [responseCode, setResponseCode] = useState(null);

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const res = await fetch('/api/user/transactions');
                const data = await parseResponse(res);
                setData(data?.data ?? []);
            } catch (err) {
                console.error(err);
                setResponseCode(err.status ?? null);
                if (err.status === 401) {
                    setError("You must be logged in to view transaction history.");
                } else if (err.status === 404) {
                    setError("User not found.");
                } else if (err.status === 500) {
                    setError("Could not load transaction history. Please try again later.");
                } else {
                    setError("An unexpected error occurred. Please try again.");
                }
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [])

    return { loading, data, error, responseCode };
}
