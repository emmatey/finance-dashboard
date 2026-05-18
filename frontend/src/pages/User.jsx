import { useParams } from 'react-router-dom'
import Header from '../components/Header.jsx'
import Footer from '../components/Footer.jsx'
import UserBody from '../components/UserBody.jsx'

export default function User() {
    const { username } = useParams()

    return (
        <>
            <Header />
            <UserBody username={username} />
            <Footer />
        </>
    )
}
