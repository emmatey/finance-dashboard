import { useNavigate } from 'react-router-dom'
import SearchBar from '../components/search/SearchBar.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export default function Header() {
    const navigate = useNavigate()
    const { user, logout } = useAuth();

    return (
        <header style={{ display: 'flex' }}>
            <span onClick={() => navigate('/')}>
                Finance Dashboard
            </span>

            <SearchBar />
            
            <div>
                {user
                    ?
                    (
                        <div>
                            <button aria-label='logout' onClick={logout}> Log Out </button>
                            <button aria-label="User"> {user} </button>
                        </div>
                    )
                    :
                    (
                        <button type='button' onClick={() => navigate('/auth?mode=login')}> Log In </button>
                    )}
            </div>
        </header>
    )
}
