import Header from '../components/Header.jsx'
import Footer from '../components/Footer.jsx'
import '../styles/utilities.css'


export default function Search() {
    const [searchParams] = useSearchParams()
    const query = searchParams.get('q')

    return (
        <>
            <Header />
            <div className='card'>
                <SearchBody query={query} />
            </div>
            <Footer />
        </>
    )
}