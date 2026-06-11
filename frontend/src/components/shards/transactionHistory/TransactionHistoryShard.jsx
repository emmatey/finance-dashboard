import { useState, useEffect } from 'react'
import { parseResponse } from '../../../scripts/utils.js'
import '../../../styles/utilities.css'
import '../../../styles/colors.css'


export default function TransactionHistoryShard({ username }) {
    const [historyObjects, setHistoryObjects] = useState([]);
    const [loading, setLoading] = useState(false);

    async function fetchHistory() {
        const safeQuery = String(username).trim();
        try {
            const response = await fetch(`/api/user/transactions?username=${encodeURIComponent(safeQuery)}`);
            return (await parseResponse(response))?.data ?? [];
        } catch (error) {
            console.error(error);
            return [];
        }
    }

    useEffect(() => {
        if (username === undefined) {
            setLoading(true);
        } else if (username) {
            setLoading(false);
            fetchHistory().then(setHistoryObjects);
        }
    }, [username]);

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