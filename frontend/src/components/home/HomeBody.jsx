import Header from '../Header.jsx'
import Footer from '../Footer.jsx'
import ScreenerShard from '../shards/screener/ScreenerShard.jsx'
import TransactionHistoryShard from '../shards/transactionHistory/TransactionHistoryShard.jsx'

export default function HomeBody({ username }) {
    return (
        <>
        <Header />
        <div>
            <div className='card'>
                <h1>Hi {username || null}, Welcome to finance-dashboard, you ARE logged in!</h1>
            </div>
            <TransactionHistoryShard username={username} />
        </div>
        <Footer />
        </>
    )
}
