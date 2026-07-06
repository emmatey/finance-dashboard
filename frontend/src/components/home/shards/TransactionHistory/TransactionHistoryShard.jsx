import useTransactionHistory from './useTransactionHistory.js'
import TransactionHistoryTable from './TransactionHistoryTable'


export default function TransactionHistoryShard() {
    const { loading, data, error } = useTransactionHistory();

    return (
        <div className='card'>
            {loading && (
                <span> Loading ... </span>
            )}

            {error && (
                <span> {error} </span>
            )}

            {!loading && !error && (
                <TransactionHistoryTable data={data ?? []} />
            )}
        </div>
    )
}