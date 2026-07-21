import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { formatCurrencyUSD } from '@/scripts/utils.js'

function formatAnalystRating(rating) {
    /*
        Converts a raw analyst rating string (snake_case or camelCase) into a
        human-readable title-cased label. Returns 'N/A' for falsy values.
    */
    if (!rating) return 'N/A'
    return rating
        .replace(/_/g, ' ')
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .replace(/\b\w/g, c => c.toUpperCase())
}

function getAnalystRatingColorClass(rating) {
    /*
        Maps an analyst rating string to a text color class.
        Buy-side ratings → gain, sell-side → destructive, everything else → neutral.
    */
    if (!rating) return ''
    const r = rating.toLowerCase()
    if (r.includes('buy')) return 'text-gain'
    if (r.includes('sell') || r.includes('underperform')) return 'text-destructive'
    return 'text-amber-600 dark:text-amber-400'
}

export default function AnalystSentimentCard({ financialMetrics, quote }) {
    const metrics = financialMetrics?.[0];
    const lastPrice = quote?.[0]?.last_price;
    const analystUpside = metrics?.target_price != null && lastPrice != null
        ? ((metrics.target_price - lastPrice) / lastPrice) * 100
        : null;

    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Analyst Sentiment</CardTitle>
            </CardHeader>
            <CardContent>
                {metrics ? (
                    <>
                        <div className="mb-3">
                            <span className={`text-2xl font-bold ${getAnalystRatingColorClass(metrics.rating)}`}>
                                {formatAnalystRating(metrics.rating)}
                            </span>
                            {metrics.analyst_count != null && (
                                <span className="ml-2 text-sm text-muted-foreground">
                                    {metrics.analyst_count} analyst{metrics.analyst_count !== 1 ? 's' : ''}
                                </span>
                            )}
                        </div>
                        <div className="space-y-1.5 text-sm">
                            <div className="flex items-center justify-between border-b border-border py-1">
                                <span className="text-muted-foreground">Target Price</span>
                                <span>{formatCurrencyUSD(metrics.target_price)}</span>
                            </div>
                            <div className="flex items-center justify-between border-b border-border py-1">
                                <span className="text-muted-foreground">Current Price</span>
                                <span>{formatCurrencyUSD(lastPrice)}</span>
                            </div>
                            {analystUpside != null && (
                                <div className="flex items-center justify-between py-1">
                                    <span
                                        className="text-muted-foreground"
                                        title="How much the current price would need to move to reach the analyst consensus target. Positive = analysts expect growth, negative = analysts expect a decline."
                                    >
                                        Implied Upside ⓘ
                                    </span>
                                    <span className={`font-semibold ${analystUpside >= 0 ? 'text-gain' : 'text-destructive'}`}>
                                        {analystUpside >= 0 ? '+' : ''}{analystUpside.toFixed(1)}%
                                    </span>
                                </div>
                            )}
                        </div>
                    </>
                ) : (
                    <div className="flex items-center justify-center py-8">
                        <Spinner className="size-5" />
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
