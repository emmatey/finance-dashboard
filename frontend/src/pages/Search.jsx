import { useSearchParams } from 'react-router-dom'
import Header from '../components/Header.jsx'
import Footer from '../components/Footer.jsx'

export default function Search() {
    const [searchParams] = useSearchParams()
    const query = searchParams.get('q')

    return (
        <>
            <Header />
            <SearchBody query={query} />
            <Footer />
        </>
    )
}
