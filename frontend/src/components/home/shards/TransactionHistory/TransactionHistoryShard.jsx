import '@/styles/utilities.css'
import '@/styles/colors.css'
import useTransactionHistory from './useTransactionHistory.js'
import { useState } from 'react';


export default function TransactionHistoryShard() {
    const [historyObjects, setHistoryObjects] = useState([]);
    const [loading, setLoading] = useState(false);

    useTransactionHistory(setHistoryObjects, setLoading);
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
                        <th>Type</th>
                        <th>Ticker</th>
                        <th>Qty</th>
                        <th>Price/Share</th>
                        <th>Date</th>
                        <th>Balance After</th>
                    </tr>
                </thead>
                <tbody>
                    {historyObjects.map(tx => (
                        <tr key={tx.transaction_id}>
                            <td>{String(tx.transaction_type).toLocaleUpperCase()}</td>
                            <td>{tx.ticker}</td>
                            <td>{Math.abs(tx.qty)}</td>
                            <td>${tx.unit_price.toFixed(2)}</td>
                            <td>{tx.datetime}</td>
                            <td>${tx.cash_after.toFixed(2)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>}
        </div>
    )
}