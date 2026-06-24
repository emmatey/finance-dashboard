import usePortfolio from "./usePortfolio";


export default function PortfolioShard() {
    const { loading, data, error, responseCode } = usePortfolio();

    return (
        <div className='card'>
            {loading && (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100px' }}>
                    <span>Loading...</span>
                </div>
            )}
            {!loading && <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Name</th>
                        <th>Shares</th>
                        <th>Price/Share</th>
                        <th>Cost Basis</th>
                        <th>Current Value</th>
                        <th>Gain/Loss</th>
                        <th>Gain/Loss %</th>
                    </tr>
                </thead>
                <tbody>
                    {(data ?? []).map(h => (
                        <tr key={h.symbol}>
                            <td>{h.symbol}</td>
                            <td>{h.name}</td>
                            <td>{h.shares}</td>
                            <td>${h.unit_price.toFixed(2)}</td>
                            <td>${h.cost_basis.toFixed(2)}</td>
                            <td>${h.current_value.toFixed(2)}</td>
                            <td>${h.gain_loss.toFixed(2)}</td>
                            <td>{h.gain_loss_pct.toFixed(2)}%</td>
                        </tr>
                    ))}
                </tbody>
            </table>}
        </div>
    )
}