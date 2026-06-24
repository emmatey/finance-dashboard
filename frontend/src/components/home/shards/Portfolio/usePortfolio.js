import { useState, useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'
import { useAuth } from '@/context/AuthContext.jsx';


export default function usePortfolio() {
    const { user } = useAuth();
    const [holdingsObjects, setHoldingsObjects] = useState([])
    const [loading, setLoading] = useState(false)
    const [errorStatus, setErrorStatus] = useState(null)

    useEffect(() => {
        if (user === undefined) {
            setLoading(true)
            return
        };
        if (!user) {
            return;
        };

        async function fetchHoldings(user) {
            const url = `/api/user/portfolio?username=${encodeURIComponent(user)}`;
            try {
                const res = await fetch(url);
                const data = await parseResponse(res);
                setHoldingsObjects(data?.data ?? []);
                setLoading(false);
            } catch (error) {
                console.error(error);
                console.error(error.data);
                setLoading(false);
                setErrorStatus(error.status ?? null)
                if (error.status === 404) {
                    console.error('User not found.')
                } else if (error.status === 500) {
                    console.error('Server error fetching portfolio.')
                }
            }
        }
        fetchHoldings(user);
    }, [user])

    return { holdingsObjects, loading, errorStatus }
}