import '../../../styles/utilities.css'
import '../../../styles/colors.css'
import useTransactionHistory from './useTransactionHistory.js'


export default function TransactionHistoryShard({ username }) {
    const { historyObjects } = useTransactionHistory(username);

    return (
        <div className='card'>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Ticker</th>
                        <th>Shares</th>
                        <th>Price/Share</th>
                        <th>Date</th>
                        <th>Balance After</th>
                    </tr>
                </thead>
                <tbody>
                    {historyObjects.map(tx => (
                        <tr key={tx.transaction_id}>
                            <td>{tx.transaction_type}</td>
                            <td>{tx.ticker === 'CASH' ? '—' : tx.ticker}</td>
                            <td>{Math.abs(tx.qty)}</td>
                            <td>{tx.ticker === 'CASH' ? '—' : `$${tx.unit_price.toFixed(2)}`}</td>
                            <td>{tx.datetime}</td>
                            <td>${tx.cash_after.toFixed(2)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}