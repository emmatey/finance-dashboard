import { useState, useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'
import { useAuth } from '@/context/AuthContext.jsx';

export default function useTransactionHistory(setHistoryObjects) {
    const [user] = useAuth();

    useEffect(() => {
        if (user === undefined) {
            setLoading(true)
            return
        }
        if (!user) return

        async function fetchHistory() {
            try {
                const response = await fetch(`/api/user/transactions?username=${encodeURIComponent(user)}`)
                const data = await parseResponse(response)?.data ?? [];
                setHistoryObjects(date);
                setLoading(false);
            } catch (error) {
                console.error(error)
                return []
            }
        }
        fetchHistory()
    }, [user])
}
