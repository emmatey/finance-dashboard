export default function StockSplitsCard({ stockSplits }) {
    if (!stockSplits.length) return null
    return (
        <div className="row mb-3">
            <div className="col-12">
                <div className="card">
                    <div className="card-body">
                        <h5 className="card-title">Stock Splits</h5>
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
                    </div>
                </div>
            </div>
        </div>
    )
}
