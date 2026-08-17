import Header from '@/components/header/Header.jsx'
import UserProfile from '@/components/user/UserProfile'
import { useParams } from 'react-router-dom'


export default function User() {
    const { username } = useParams();
    return (
        <>
            <Header />
            <UserProfile username={username}/>
        </>
    )
}
