export default function StockSplitsCard({ stockSplits }) {
    return (
        <div className="card h-100">
            <div className="card-body">
                <h5 className="card-title">Stock Splits</h5>
                {stockSplits?.length > 0 ? (
                    <table className="table table-sm mb-0">
                        <thead>
                            <tr>
                                <th className="text-muted fw-normal small">Date</th>
                                <th className="text-muted fw-normal small">Ratio</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stockSplits.map((s, i) => (
                                <tr key={i}>
                                    <td className="small">{s.split_date ?? 'N/A'}</td>
                                    <td className="small">{s.split_ratio != null ? `${s.split_ratio}:1` : 'N/A'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p className="text-muted small mb-0">No stock splits on record.</p>
                )}
            </div>
        </div>
    )
}
