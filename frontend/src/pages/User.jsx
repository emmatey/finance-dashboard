import Header from '@/components/Header.jsx'
import UserShard from '@/components/user/UserShard'
import Footer from '@/components/Footer.jsx'
import { useParams } from 'react-router-dom'


export default function User() {
    const { username } = useParams();
    return (
        <>
            <Header />
            <UserShard username={username}/>
            <Footer />
        </>
    )
}
