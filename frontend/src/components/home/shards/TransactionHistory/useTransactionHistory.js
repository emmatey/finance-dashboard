import { useState, useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'
import { useAuth } from '@/context/AuthContext.jsx';

export default function useTransactionHistory() {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [responseCode, setResponseCode] = useState(null);

    useEffect(() => {
        if (user === undefined) {
            setLoading(true)
            return
        }
        if (!user) return

        async function fetchData() {
            try {
                setLoading(true);
                const res = await fetch(`/api/user/transactions?username=${encodeURIComponent(user)}`);
                const data = await parseResponse(res);
                setData(data?.data ?? []);
            } catch (err) {
                console.error(err);
                setResponseCode(err.status ?? null);
                if (err.status === 400) {
                    setError("No user session found. Please log in.");
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
    }, [user])

    return { loading, data, error, responseCode };
}
