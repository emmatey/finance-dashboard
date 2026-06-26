import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { formatCurrencyUSD } from '@/scripts/utils.js'

const SERIES = [
    { key: 'grand_total',     label: 'Account Value' },
    { key: 'portfolio_value', label: 'Holdings' },
    { key: 'cash_balance',    label: 'Balance' },
]

const COLOR_GAIN = '#16A34A'
const COLOR_LOSS = '#FF534C'

export default function BalanceHistoryChart({ snapshots }) {
    const canvasRef = useRef(null)
    const chartRef = useRef(null)
    const [activeSeries, setActiveSeries] = useState('grand_total')

    const datetimes = snapshots.map(s => s.snap_datetime)
    const dates = datetimes.map(dt => dt.match(/\d{4}-\d{2}-\d{2}/)?.[0] ?? dt)

    // Create chart on mount / when snapshot data changes
    useEffect(() => {
        if (!canvasRef.current || !snapshots.length) return
        const Chart = window.Chart
        if (!Chart) return

        if (chartRef.current) chartRef.current.destroy()

        const values = snapshots.map(s => s[activeSeries])
        const isGain = values.at(-1) >= values[0]

        chartRef.current = new Chart(canvasRef.current, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: SERIES.find(s => s.key === activeSeries)?.label,
                    data: values,
                    borderColor: isGain ? COLOR_GAIN : COLOR_LOSS,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        displayColors: false,
                        callbacks: {
                            title: ctx => datetimes[ctx[0].dataIndex],
                            label: ctx => formatCurrencyUSD(ctx.parsed.y),
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
    }, [snapshots])

    // Update chart in-place when switching series (no recreate)
    useEffect(() => {
        if (!chartRef.current || !snapshots.length) return

        const values = snapshots.map(s => s[activeSeries])
        const isGain = values.at(-1) >= values[0]
        const ds = chartRef.current.data.datasets[0]

        ds.label = SERIES.find(s => s.key === activeSeries)?.label
        ds.data = values
        ds.borderColor = isGain ? COLOR_GAIN : COLOR_LOSS
        chartRef.current.update()
    }, [activeSeries])

    return (
        <div>
            <div className="relative w-full" style={{ height: '260px' }}>
                <canvas ref={canvasRef} />
            </div>
            <div className="flex justify-center gap-2 mt-3">
                {SERIES.map(({ key, label }) => (
                    <Button
                        key={key}
                        size="sm"
                        variant={activeSeries === key ? 'default' : 'outline'}
                        className="rounded-lg"
                        onClick={() => setActiveSeries(key)}
                    >
                        {label}
                    </Button>
                ))}
            </div>
        </div>
    )
}
