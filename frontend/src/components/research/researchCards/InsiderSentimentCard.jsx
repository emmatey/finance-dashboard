import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import SentimentBar from './SentimentBar.jsx'

function getSentimentLabel(score) {
    /*
        Converts a numeric insider sentiment score in the range [-1, 1] to a
        human-readable label. Returns 'No Data' for null or undefined values.
    */
    if (score == null) return 'No Data'
    if (score > 0.5) return 'Strongly Bullish'
    if (score > 0.15) return 'Bullish'
    if (score > -0.15) return 'Neutral'
    if (score > -0.5) return 'Bearish'
    return 'Strongly Bearish'
}

function getSentimentColorClass(score) {
    /*
        Maps a numeric insider sentiment score to a text color class.
        Returns a neutral color for null or undefined values.
    */
    if (score == null) return 'text-muted-foreground'
    if (score > 0.15) return 'text-gain'
    if (score < -0.15) return 'text-destructive'
    return 'text-amber-600 dark:text-amber-400'
}

export default function InsiderSentimentCard({ financialMetrics }) {
    const metrics = financialMetrics?.[0];
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Insider Sentiment</CardTitle>
            </CardHeader>
            <CardContent>
                {metrics ? (
                    <>
                        <div className="mb-2">
                            <span className={`text-2xl font-bold ${getSentimentColorClass(metrics.insider_sentiment)}`}>
                                {getSentimentLabel(metrics.insider_sentiment)}
                            </span>
                            {metrics.insider_sentiment != null && (
                                <span className="ml-2 text-sm text-muted-foreground">
                                    score: {Number(metrics.insider_sentiment).toFixed(3)}
                                </span>
                            )}
                        </div>
                        <SentimentBar score={metrics.insider_sentiment} />
                        <p className="mt-2 text-sm text-muted-foreground">
                            Based on open-market insider trades in the past 12 months. Buys are weighted over sells.
                        </p>
                    </>
                ) : (
                    <p className="text-sm text-muted-foreground">Loading…</p>
                )}
            </CardContent>
        </Card>
    )
}
