import { useState, useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'

export default function useTickerInfo(activeQuery) {
    const [tickerInfoJson, setTickerInfoJson] = useState(null)
    const [loading, setLoading] = useState(false)

    async function fetchTickerInfo(query) {
        try {
            setLoading(true)
            const response = await fetch(`/api/trade?ticker=${encodeURIComponent(query)}`)
            const json = await parseResponse(response) || {}
            setTickerInfoJson(json)
            setLoading(false)
            return true
        } catch (error) {
            setLoading(false)
            if (error.status === 404) {
                console.log(`Ticker ${query} not found.`)
                setTickerInfoJson(null)
                return false
            }
            if (error.status === 401) {
                setTickerInfoJson({ error: 'Session expired. Please log in again.' })
                return false
            }
            setTickerInfoJson({ error: `${error}` })
            console.error(error)
            return false
        }
    }

    useEffect(() => {
        if (!activeQuery) {
            setTickerInfoJson(null)
            setLoading(false)
            return
        }

        let timerId = null

        async function tick() {
            const ok = await fetchTickerInfo(activeQuery)
            if (ok) {
                timerId = setTimeout(() => {
                    console.log(`Price of ${activeQuery} updated.`)
                    tick()
                }, 60000)
            }
        }

        tick()

        return () => { clearTimeout(timerId) }
    }, [activeQuery])

    return { tickerInfoJson, loading }
}
