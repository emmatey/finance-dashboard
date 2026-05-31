import { useNavigate } from 'react-router-dom'
import SearchBar from './SearchBar.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export default function Header() {
    const navigate = useNavigate()
    const {user, logout} = useAuth();

    return (
        <header>
            <span onClick={() => navigate('/')}>
                Finance Dashboard
            </span>
            <div>
                <SearchBar />
                {user
                ?
                (<button aria-label="User"/>)
                :
                (<button
                    type='button'
                    onClick={() => navigate('/login')}
                    >
                    Log In
                </button>)}
            </div>
        </header>
    )
}
