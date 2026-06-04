import Header from '../Header.jsx'
import Footer from '../Footer.jsx'
import Screeners from '../screener/Screeners.jsx'

export default function HomeBody({ username }) {
    return (
        <>
        <Header />
        <div>
            <div className='card'>
                <h1>Hi {username || null}, Welcome to finance-dashboard, you ARE logged in!</h1>
            </div>
            <Screener />
        </div>
        <Footer />
        </>
    )
}
