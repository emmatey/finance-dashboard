import Header from '../Header.jsx'
import Footer from '../Footer.jsx'
import TradeShard from '../home/shards/Trade/TradeShard.jsx'
import Scratchpad from '../../Scratchpad.jsx'
import MarketOverviewShard from '../home/shards/MarketOverview/MarketOverviewShard.jsx'

export default function HomeBody({ username }) {
    return (
        <>
        <Header />
        <div>
            <MarketOverviewShard />
            <div className='card'>
                <h1>Hi {username || null}, Welcome to finance-dashboard, you ARE logged in!</h1>
            </div>
        </div>
        <Footer />
        </>
    )
}
