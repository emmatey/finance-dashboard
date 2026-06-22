import { useState, useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'

export default function useResearchData(ticker) {
    const [data, setData] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!ticker) return
        setData(null)
        setError(null)

        let cancelled = false

        async function load() {
            try {
                const localRes = await fetch(`/api/research/local?ticker=${encodeURIComponent(ticker)}`)
                const local = await parseResponse(localRes)
                if (!cancelled) setData(local)
            } catch {
                // ticker may not be in DB yet — continue to online fetch
            }

            try {
                const onlineRes = await fetch(`/api/research/online?ticker=${encodeURIComponent(ticker)}`)
                const online = await parseResponse(onlineRes)
                if (!cancelled) setData(online)
            } catch (err) {
                if (!cancelled) setError(err.message)
            }
        }

        load()
        return () => { cancelled = true }
    }, [ticker])

    return { data, error }
}
