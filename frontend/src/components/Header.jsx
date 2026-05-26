import { useNavigate } from 'react-router-dom'
import SearchBar from './SearchBar.jsx'
import '../styles/Header.css'
import { useAuth } from '../context/AuthContext.jsx'

export default function Header() {
    const navigate = useNavigate()
    const {user, login, logout} = useAuth();

    return (
        <header>
            <span className="header-logo" onClick={() => navigate('/')}>
                Finance Dashboard
            </span>
            <div className="header-right">
                <SearchBar />
                {user 
                ? 
                (<button className="header-user-btn" aria-label="User"/>)
                :
                (<button
                    type='button'
                    className='btn btn-primary' 
                    onClick={() => navigate('/login')}
                    > 
                    Log In
                </button>)}
            </div>
        </header>
    )
}
