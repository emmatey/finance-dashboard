import Header from '@/components/Header.jsx'
import Footer from '@/components/Footer.jsx'
import TradeShard from '@/components/home/shards/Trade/TradeShard.jsx'
import Scratchpad from '@/Scratchpad.jsx'
import MarketOverviewShard from '@/components/home/shards/MarketOverview/MarketOverviewShard.jsx'
import TransactionHistoryShard from './shards/TransactionHistory/TransactionHistoryShard.jsx'


export default function HomeBody({ username }) {
    return (
        <>
        <Header />
        <div>
            <TransactionHistoryShard />
            <div className='card'>
                <h1>Hi {username || null}, Welcome to finance-dashboard, you ARE logged in!</h1>
            </div>
        </div>
        <Footer />
        </>
    )
}
