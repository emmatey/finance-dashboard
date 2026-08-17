import Header from '@/components/header/Header.jsx'
import SearchBody from '@/components/search/SearchBody.jsx'
import { useSearchParams } from 'react-router-dom'



export default function Search() {
    const [searchParams] = useSearchParams()
    const query = searchParams.get('q')

    return (
        <>
            <Header />
            <SearchBody query={query} />
        </>
    )
}