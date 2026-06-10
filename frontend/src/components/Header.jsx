import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { getRandomIntInclusive } from '../scripts/utils.js'

import SearchBar from '../components/search/SearchBar.jsx'

import '../styles/colors.css'
import '../styles/utilities.css'

export default function Header() {
    const navigate = useNavigate()
    const { user, logout } = useAuth();

    function handleMouseOver(event) {
        const span = event.currentTarget.querySelector('span');
        const val = getRandomIntInclusive(1, 4);
        if (val === 1) {
            span.style.color = 'var(--blue-3)';
        } else if (val === 2) {
            span.style.color = 'var(--yellow-4)';
        } else if (val === 3) {
            span.style.color = 'var(--red-3)';
        } else if (val === 4) {
            span.style.color = 'var(--green-3)';
        } else {
            throw new Error("invalid 'val' var in header.jsx");
        };
    }

    function handleMouseLeave(event) {
        const span = event.currentTarget.querySelector('span');
        span.style.color = '#000000';
    }

    return (
        <header style={{ display: 'flex' }}>
            
            <div onClick={() => navigate('/')} onMouseOver={handleMouseOver} onMouseLeave={handleMouseLeave} style={{ cursor: 'pointer' }}>
                <span>Finance Dashboard</span>
            </div>

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