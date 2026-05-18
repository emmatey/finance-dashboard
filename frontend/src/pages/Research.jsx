import { useSearchParams } from 'react-router-dom'
import Header from '../components/Header.jsx'
import Footer from '../components/Footer.jsx'
import ResearchBody from '../components/ResearchBody.jsx'

export default function Research() {
    const [searchParams] = useSearchParams()
    const ticker = searchParams.get('ticker')

    return (
        <>
            <Header />
            <ResearchBody ticker={ticker} />
            <Footer />
        </>
    )
}
