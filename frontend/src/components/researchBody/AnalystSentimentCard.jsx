import { formatCurrencyUSD, formatAnalystRating, getAnalystRatingColorClass } from '../../scripts/utils.js'

export default function AnalystSentimentCard({ metrics, lastPrice, analystUpside }) {
    return (
        <div className="card h-100">
            <div className="card-body">
                <h5 className="card-title">Analyst Sentiment</h5>
                {metrics ? (
                    <>
                        <div className="mb-3">
                            <span className={`fw-bold fs-4 ${getAnalystRatingColorClass(metrics.rating)}`}>
                                {formatAnalystRating(metrics.rating)}
                            </span>
                            {metrics.analyst_count != null && (
                                <span className="text-muted small ms-2">
                                    {metrics.analyst_count} analyst{metrics.analyst_count !== 1 ? 's' : ''}
                                </span>
                            )}
                        </div>
                        <table className="table table-sm mb-0">
                            <tbody>
                                <tr>
                                    <th className="text-muted fw-normal small">Target Price</th>
                                    <td className="small">{formatCurrencyUSD(metrics.target_price)}</td>
                                </tr>
                                <tr>
                                    <th className="text-muted fw-normal small">Current Price</th>
                                    <td className="small">{formatCurrencyUSD(lastPrice)}</td>
                                </tr>
                                {analystUpside != null && (
                                    <tr>
                                        <th className="text-muted fw-normal small">
                                            <span title="How much the current price would need to move to reach the analyst consensus target. Positive = analysts expect growth, negative = analysts expect a decline.">
                                                Implied Upside ⓘ
                                            </span>
                                        </th>
                                        <td className={`small fw-semibold ${analystUpside >= 0 ? 'text-success' : 'text-danger'}`}>
                                            {analystUpside >= 0 ? '+' : ''}{analystUpside.toFixed(1)}%
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </>
                ) : (
                    <p className="text-muted small mb-0">Loading…</p>
                )}
            </div>
        </div>
    )
}
