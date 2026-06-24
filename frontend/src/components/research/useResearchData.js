import { useState, useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'

export default function useResearchData(ticker) {
    const [data, setData] = useState(null)
    const [errorStatus, setErrorStatus] = useState(null)

    useEffect(() => {
        if (!ticker) return
        setData(null)
        setErrorStatus(null)

        let cancelled = false

        async function load() {
            try {
                const localRes = await fetch(`/api/research/local?ticker=${encodeURIComponent(ticker)}`)
                const local = await parseResponse(localRes)
                if (!cancelled) setData(local)
            } catch (err) {
                // local failure (e.g. 500 db error) — still attempt online fetch
                if (!cancelled) console.error('Local research fetch failed:', err)
            }

            try {
                const onlineRes = await fetch(`/api/research/online?ticker=${encodeURIComponent(ticker)}`)
                const online = await parseResponse(onlineRes)
                if (!cancelled) setData(online)
            } catch (err) {
                if (!cancelled) {
                    setErrorStatus(err.status ?? null)
                    if (err.status === 404) {
                        console.error(`Ticker ${ticker} not found.`)
                    } else if (err.status === 500) {
                        console.error('Server error fetching research data.')
                    } else {
                        console.error(err)
                    }
                }
            }
        }

        load()
        return () => { cancelled = true }
    }, [ticker])

    return { data, errorStatus }
}
