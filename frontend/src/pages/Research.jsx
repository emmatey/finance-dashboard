import { useSearchParams } from 'react-router-dom'
import Header from '@/components/Header.jsx'
import Footer from '@/components/Footer.jsx'
import ResearchShard from '@/components/research/ResearchShard'

export default function Research() {
    const [searchParams] = useSearchParams()
    const ticker = searchParams.get('ticker')

    return (
        <>
            <Header />
            <ResearchShard ticker={ticker} />
            <Footer />
        </>
    )
}
