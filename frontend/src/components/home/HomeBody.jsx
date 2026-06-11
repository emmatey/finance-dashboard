import Header from '../Header.jsx'
import Footer from '../Footer.jsx'
import ScreenerShard from '../shards/screener/ScreenerShard.jsx'
import TransactionHistoryShard from '../shards/transactionHistory/TransactionHistoryShard.jsx'
import TradeShard from '../shards/trade/TradeShard.jsx'

export default function HomeBody({ username }) {
    return (
        <>
        <Header />
        <div>
            <div className='card'>
                <h1>Hi {username || null}, Welcome to finance-dashboard, you ARE logged in!</h1>
            </div>
            <TransactionHistoryShard username={username} />
            <TradeShard />
        </div>
        <Footer />
        </>
    )
}
