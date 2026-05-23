import { useState, useEffect } from 'react'

export default function ScreenerCard() {
    const [screenerData, setScreenerData] = useState({})

    useEffect(() => {
        const controller = new AbortController()

        async function fetchScreeners() {
            try {
                const response = await fetch('/api/screeners', { signal: controller.signal })
                if (!response.ok) {
                    console.error('Screener fetch failed:', response.status)
                    setScreenerData({})
                    return
                }
                const data = await response.json()
                console.info('Screeners loaded:', data)
                setScreenerData(data)
            } catch (err) {
                if (err.name === 'AbortError') return
                console.error('Failed to fetch screeners:', err)
                setScreenerData({})
            }
        }

        fetchScreeners()
        return () => controller.abort()
    }, [])

    return (
        <ul>
            {Object.entries(screenerData).map(([screenerName, companies]) => {
                if (!Array.isArray(companies)) return null
                return (
                    <li key={screenerName}>
                        <strong>{screenerName}</strong>
                        <ul>
                            {companies.map((company, i) => (
                                <li key={i}>{JSON.stringify(company)}</li>
                            ))}
                        </ul>
                    </li>
                )
            })}
        </ul>
    )
}
