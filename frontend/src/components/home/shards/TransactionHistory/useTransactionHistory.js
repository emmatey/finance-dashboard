import { useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'
import { useAuth } from '@/context/AuthContext.jsx';

export default function useTransactionHistory(setHistoryObjects, setLoading) {
    const { user } = useAuth();

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
                return []
            }
        }
        fetchHistory()
    }, [user])
}
