import { useEffect, useRef, useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'

const RANGES = { '1yr': 31536000, '1mo': 2592000, '1wk': 604800 }

function getSubsetIdx(timestamps, timeDelta) {
    const now = Math.floor(Date.now() / 1000)
    const target = now - timeDelta
    for (const [idx, ts] of timestamps.entries()) {
        if (ts >= target) return idx
    }
    return timestamps.length
}

export default function PriceChartCard({ prices }) {
    const canvasRef = useRef(null)
    const chartRef = useRef(null)
    const [range, setRange] = useState('1yr')

    const sorted = prices?.length
        ? [...prices].sort((a, b) => a.timestamp - b.timestamp)
        : []

    useEffect(() => {
        if (!sorted.length || !canvasRef.current) return

        const Chart = window.Chart
        if (!Chart) return

        const idx = getSubsetIdx(sorted.map(p => p.timestamp), RANGES[range])
        const data = sorted.slice(idx).length > 0 ? sorted.slice(idx) : sorted

        const labels = data.map(d => new Date(d.timestamp * 1000).toLocaleDateString())
        const openPrices = data.map(d => d.price)
        const volumes = data.map(d => d.volume)
        const isGain = openPrices[openPrices.length - 1] >= openPrices[0]
        const lineColor = isGain ? '#16A34A' : '#FF534C'

        if (chartRef.current) chartRef.current.destroy()

        chartRef.current = new Chart(canvasRef.current, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Open Price',
                    data: openPrices,
                    borderColor: lineColor,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: `Open Price — ${range}` },
                    legend: { display: false },
                    tooltip: {
                        displayColors: false,
                        callbacks: {
                            label: ctx => {
                                const price = Number(ctx.parsed.y).toLocaleString('en-US', { style: 'currency', currency: 'USD' })
                                return `Open: ${price}`
                            },
                            afterBody: ctx => {
                                const vol = volumes[ctx[0].dataIndex]
                                return vol != null ? `Volume: ${Number(vol).toLocaleString()}` : ''
                            }
                        }
                    }
                },
                scales: {
                    x: { ticks: { maxTicksLimit: 8 } },
                    y: { ticks: { callback: v => '$' + Number(v).toLocaleString() } }
                }
            }
        })

        return () => {
            chartRef.current?.destroy()
            chartRef.current = null
        }
    }, [sorted, range])

    return (
        <Card className="h-full">
            <CardContent>
                {!prices?.length ? (
                    <p className="text-sm text-muted-foreground">No price history available.</p>
                ) : (
                    <>
                        <canvas ref={canvasRef} />
                        <ToggleGroup
                            type="single"
                            variant="outline"
                            className="mx-auto mt-2"
                            value={range}
                            onValueChange={(value) => value && setRange(value)}
                        >
                            {Object.keys(RANGES).map(r => (
                                <ToggleGroupItem key={r} value={r} aria-label={`Show ${r} range`}>
                                    {r}
                                </ToggleGroupItem>
                            ))}
                        </ToggleGroup>
                    </>
                )}
            </CardContent>
        </Card>
    )
}
