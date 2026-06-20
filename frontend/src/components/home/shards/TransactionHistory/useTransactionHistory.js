import { useState, useEffect } from 'react'
import { parseResponse } from '../../../scripts/utils.js'

export default function useTransactionHistory(username) {
    const [historyObjects, setHistoryObjects] = useState([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (username === undefined) {
            setLoading(true)
            return
        }
        if (!username) return

        setLoading(false)

        async function fetchHistory() {
            const safeQuery = String(username).trim()
            try {
                const response = await fetch(`/api/user/transactions?username=${encodeURIComponent(safeQuery)}`)
                return (await parseResponse(response))?.data ?? []
            } catch (error) {
                console.error(error)
                return []
            }
        }

        fetchHistory().then(setHistoryObjects)
    }, [username])

    return { historyObjects, loading }
}
