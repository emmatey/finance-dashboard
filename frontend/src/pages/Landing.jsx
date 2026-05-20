import Header from '../components/Header.jsx'
import Footer from '../components/Footer.jsx'

export default function Landing() {
    return (
        <>
        <Header />
        <div className='container'>
            <div className='row'>
                <div className='col'>
                    <div className='row mt-4'>
                        <h1>Welcome to finance-dashboard</h1>
                    </div>
                </div>
            </div>
        </div>
        <Footer />
        </>
    )
}
