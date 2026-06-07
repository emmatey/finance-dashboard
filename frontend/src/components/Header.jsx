import { useNavigate } from 'react-router-dom'
import SearchBar from '../components/nav/SearchBar.jsx'
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
                (
                <div>
                <button aria-label='logout' onClick={logout}> Log Out </button>
                <button aria-label="User"> {user} </button>
                </div>
                )
                :
                (<button
                    type='button'
                    onClick={() => navigate('/auth?mode=login')}
                    >
                    Log In
                </button>)}
            </div>
        </header>
    )
}
