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
        Maps an analyst rating string to a Bootstrap text color utility class.
        Buy-side ratings → success, sell-side → danger, everything else → warning.
    */
    if (!rating) return ''
    const r = rating.toLowerCase()
    if (r.includes('buy')) return 'text-success'
    if (r.includes('sell') || r.includes('underperform')) return 'text-danger'
    return 'text-warning'
}

export default function AnalystSentimentCard({ financialMetrics, quote }) {
    const metrics = financialMetrics?.[0];
    const lastPrice = quote?.[0]?.last_price;
    const analystUpside = metrics?.target_price != null && lastPrice != null
        ? ((metrics.target_price - lastPrice) / lastPrice) * 100
        : null;

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
