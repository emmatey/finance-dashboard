import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { formatCurrencyUSD, formatPercent, formatNumber } from '@/scripts/utils.js'

function formatLargeNumber(n) {
    /*
        Abbreviates large numbers using T/B/M suffixes (e.g. 2500000000 → "2.50B").
        Falls back to locale-formatted output for values under 1 million.
        Returns 'N/A' for null or undefined values.
    */
    if (n == null) return 'N/A'
    const abs = Math.abs(n)
    if (abs >= 1e12) return (n / 1e12).toFixed(2) + 'T'
    if (abs >= 1e9) return (n / 1e9).toFixed(2) + 'B'
    if (abs >= 1e6) return (n / 1e6).toFixed(2) + 'M'
    return Number(n).toLocaleString('en-US')
}

export default function FinancialMetricsCard({ metrics }) {
    const metricsData = metrics?.[0];
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Financial Metrics</CardTitle>
            </CardHeader>
            <CardContent>
                {metricsData ? (
                    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                        {[
                            ['Market Cap', formatLargeNumber(metricsData.market_cap)],
                            ['EPS', formatCurrencyUSD(metricsData.eps)],
                            ['Beta', formatNumber(metricsData.beta)],
                            ['Trailing P/E', formatNumber(metricsData.trailing_pe)],
                            ['Forward P/E', formatNumber(metricsData.forward_pe)],
                            ['Profit Margin', formatPercent(metricsData.profit_margin)],
                            ['Dividend Yield', formatPercent(metricsData.dividend_yield)],
                            ['52-wk High', formatCurrencyUSD(metricsData.fifty_two_week_high)],
                            ['52-wk Low', formatCurrencyUSD(metricsData.fifty_two_week_low)],
                            ['50-day Avg', formatCurrencyUSD(metricsData.fifty_day_average)],
                            ['200-day Avg', formatCurrencyUSD(metricsData.two_hundred_day_average)],
                            ['Price / Book', formatNumber(metricsData.price_to_book)],
                            ['Book Value', formatCurrencyUSD(metricsData.book_value)],
                            ['Shares Out.', formatLargeNumber(metricsData.shares_outstanding)],
                            ['Current Ratio', formatNumber(metricsData.current_ratio)],
                            ['Debt / Equity', formatNumber(metricsData.debt_to_equity)],
                            ["Today's Vol.", formatLargeNumber(metricsData.todays_volume)],
                            ['10-day Avg Vol', formatLargeNumber(metricsData.ten_day_avg_volume)],
                            ['3-mo Avg Vol', formatLargeNumber(metricsData.three_month_avg_volume)],
                        ].map(([label, value]) => (
                            <div key={label} className="border-b border-border pb-1.5">
                                <div className="text-xs text-muted-foreground">{label}</div>
                                <div className="text-sm font-medium">{value}</div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="flex items-center justify-center py-8">
                        <Spinner className="size-5" />
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
