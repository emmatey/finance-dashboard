import { getSentimentColorClass, getSentimentLabel } from '../../scripts/utils.js'
import SentimentBar from '../SentimentBar.jsx'

export default function InsiderSentimentCard({ metrics }) {
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
