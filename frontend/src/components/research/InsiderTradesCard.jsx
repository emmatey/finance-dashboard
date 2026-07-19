import { formatNumber, formatCurrencyUSD } from '@/scripts/utils.js'

export default function InsiderTradesCard({ insiderTrades }) {
    return (
        <div className="card h-100">
            <div className="card-body">
                <h5 className="card-title">Insider Trades</h5>
                {insiderTrades.length > 0 ? (
                    <div className="table-responsive overflow-auto" style={{ maxHeight: '400px' }}>
                        <table className="table table-sm mb-0">
                            <thead>
                                <tr>
                                    {['Date', 'Filer', 'Relation', 'Shares', 'Value', 'Transaction'].map(h => (
                                        <th key={h} className="text-muted fw-normal small">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {insiderTrades.map((t, i) => (
                                    <tr key={i}>
                                        <td className="small">{t.transaction_date ?? 'N/A'}</td>
                                        <td className="small">{t.filer_name ?? 'N/A'}</td>
                                        <td className="small">{t.filer_relation ?? 'N/A'}</td>
                                        <td className="small">{t.shares != null ? formatNumber(t.shares, 0) : 'N/A'}</td>
                                        <td className="small">{formatCurrencyUSD(t.transaction_value)}</td>
                                        <td className="small">{t.transaction_text ?? 'N/A'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p className="text-muted small mb-0">No insider trades available.</p>
                )}
            </div>
        </div>
    )
}
