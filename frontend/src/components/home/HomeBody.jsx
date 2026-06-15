import Header from '../Header.jsx'
import Footer from '../Footer.jsx'
import TradeShard from '../home/shards/trade/TradeShard.jsx'
import Scratchpad from '../../Scratchpad.jsx'

export default function HomeBody({ username }) {
    return (
        <>
        <Header />
        <Scratchpad />
        <div>
            <div className='card'>
                <h1>Hi {username || null}, Welcome to finance-dashboard, you ARE logged in!</h1>
            </div>
            <TradeShard />
        </div>
        <Footer />
        </>
    )
}
