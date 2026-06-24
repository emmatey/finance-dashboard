import { useState, useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'
import { useAuth } from '@/context/AuthContext.jsx';

export default function useTransactionHistory(setHistoryObjects, setLoading) {
    const { user } = useAuth();
    const [errorStatus, setErrorStatus] = useState(null)

    useEffect(() => {
        if (user === undefined) {
            setLoading(true)
            return
        }
        if (!user) return

        async function fetchHistory() {
            try {
                const response = await fetch(`/api/user/transactions?username=${encodeURIComponent(user)}`)
                const data = await parseResponse(response);
                setHistoryObjects(data?.data ?? []);
                setLoading(false);
            } catch (error) {
                console.error(error)
                setLoading(false)
                setErrorStatus(error.status ?? null)
                if (error.status === 401) {
                    console.error('Session expired.')
                } else if (error.status === 404) {
                    console.error('User not found.')
                } else if (error.status === 500) {
                    console.error('Server error fetching transaction history.')
                }
            }
        }
        fetchHistory()
    }, [user])

    return { errorStatus }
}
