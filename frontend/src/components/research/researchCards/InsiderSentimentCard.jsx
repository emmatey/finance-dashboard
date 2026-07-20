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
        Maps a numeric insider sentiment score to a Bootstrap text color utility class.
        Returns 'text-muted' for null or undefined values.
    */
    if (score == null) return 'text-muted'
    if (score > 0.15) return 'text-success'
    if (score < -0.15) return 'text-danger'
    return 'text-warning'
}

export default function InsiderSentimentCard({ financialMetrics }) {
    const metrics = financialMetrics?.[0];
    return (
        <div className="card h-100">
            <div className="card-body">
                <h5 className="card-title">Insider Sentiment</h5>
                {metrics ? (
                    <>
                        <div className="mb-2">
                            <span className={`fw-bold fs-4 ${getSentimentColorClass(metrics.insider_sentiment)}`}>
                                {getSentimentLabel(metrics.insider_sentiment)}
                            </span>
                            {metrics.insider_sentiment != null && (
                                <span className="text-muted small ms-2">
                                    score: {Number(metrics.insider_sentiment).toFixed(3)}
                                </span>
                            )}
                        </div>
                        <SentimentBar score={metrics.insider_sentiment} />
                        <p className="text-muted small mt-2 mb-0">
                            Based on open-market insider trades in the past 12 months. Buys are weighted over sells.
                        </p>
                    </>
                ) : (
                    <p className="text-muted small mb-0">Loading…</p>
                )}
            </div>
        </div>
    )
}
