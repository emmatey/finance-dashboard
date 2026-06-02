import Header from '../components/Header.jsx'
import Footer from '../components/Footer.jsx'
import HomeBody from '../components/home/HomeBody.jsx'
import Landing from '../components/home/Landing.jsx'

import { useAuth } from '../context/AuthContext.jsx'

export default function Home() {
    const {user, logout} = useAuth();
    return (
        <>
        {user ? <HomeBody username={user}/> : <Landing />}
        </>
    )
}
