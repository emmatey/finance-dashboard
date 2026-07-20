import { useMemo, useState } from 'react'
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { formatUTCSeconds, formatCurrencyUSD } from '@/scripts/utils.js'

const RANGES = { '5yr': 31536000 * 5, '1yr': 31536000, '1mo': 2592000, '1wk': 604800 }

// Single-series config just to satisfy ChartContainer's API; the line's
// actual stroke color is set dynamically below (green/red by direction).
const CHART_CONFIG = {
    price: { label: 'Open Price' }
}

function getSubsetIdx(timestamps, timeDelta) {
    const now = Math.floor(Date.now() / 1000)
    const target = now - timeDelta
    for (const [idx, ts] of timestamps.entries()) {
        if (ts >= target) return idx
    }
    return timestamps.length
}

export default function PriceChartCard({ prices }) {
    const [range, setRange] = useState('5yr')

    const sorted = useMemo(
        () => (prices?.length ? [...prices].sort((a, b) => a.timestamp - b.timestamp) : []),
        [prices]
    )

    const rangedData = useMemo(() => {
        if (!sorted.length) return []
        const idx = getSubsetIdx(sorted.map(p => p.timestamp), RANGES[range])
        const subset = sorted.slice(idx)
        return subset.length > 0 ? subset : sorted
    }, [sorted, range])

    const isGain = rangedData.length > 1 && rangedData[rangedData.length - 1].price >= rangedData[0].price
    const lineColor = isGain ? 'var(--color-gain)' : 'var(--color-destructive)'

    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Price History</CardTitle>
            </CardHeader>
            <CardContent>
                {!rangedData.length ? (
                    <p className="text-sm text-muted-foreground">No price history available.</p>
                ) : (
                    <>
                        <ChartContainer config={CHART_CONFIG} className="h-56 w-full">
                            <LineChart data={rangedData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis
                                    dataKey="timestamp"
                                    tickFormatter={formatUTCSeconds}
                                    tickLine={false}
                                    axisLine={false}
                                />
                                <YAxis
                                    tickFormatter={formatCurrencyUSD}
                                    tickLine={false}
                                    axisLine={false}
                                    width={80}
                                />
                                <ChartTooltip
                                    content={
                                        <ChartTooltipContent
                                            labelFormatter={(_, payload) => formatUTCSeconds(payload?.[0]?.payload?.timestamp)}
                                            formatter={(value, _name, item) => (
                                                <div className="flex w-full flex-col gap-0.5">
                                                    <div className="flex items-center justify-between gap-4">
                                                        <span className="text-muted-foreground">Open</span>
                                                        <span className="font-mono font-medium text-foreground">{formatCurrencyUSD(value)}</span>
                                                    </div>
                                                    {item.payload.volume != null && (
                                                        <div className="flex items-center justify-between gap-4">
                                                            <span className="text-muted-foreground">Volume</span>
                                                            <span className="font-mono font-medium text-foreground">{Number(item.payload.volume).toLocaleString()}</span>
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        />
                                    }
                                />
                                <Line
                                    dataKey="price"
                                    type="monotone"
                                    stroke={lineColor}
                                    strokeWidth={2}
                                    dot={false}
                                />
                            </LineChart>
                        </ChartContainer>
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
