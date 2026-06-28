import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext.jsx'
import { getRandomAccentColor } from '@/scripts/utils.js'

import SearchBar from '@/components/search/SearchBar.jsx'

import '@/styles/colors.css'
import '@/styles/utilities.css'

export default function Header() {
    const navigate = useNavigate()
    const { user, logout } = useAuth();

    function handleMouseOver(event) {
        const span = event.currentTarget.querySelector('span');
        span.style.color = getRandomAccentColor();
    }

    function handleMouseLeave(event) {
        const span = event.currentTarget.querySelector('span');
        span.style.color = '#000000';
    }

    return (
        <header>
            <div className='flex'>
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
            </div>
        </header>
    )
}