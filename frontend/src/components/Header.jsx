import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext.jsx'
import { useShardNav } from '@/context/ShardNavContext.jsx'
import { getRandomAccentColor } from '@/scripts/utils.js'
import { Button } from '@/components/ui/button'

import SearchBar from '@/components/search/SearchBar.jsx'

import '@/styles/colors.css'
import '@/styles/utilities.css'

export default function Header() {
    const navigate = useNavigate()
    const { user, logout } = useAuth();
    // null on pages rendered outside HomeBody's ShardNavProvider (Research, User, Search, ...)
    const shardNav = useShardNav();

    function goHome() {
        shardNav?.setActiveGroupId('home');
        navigate('/');
    }

    function handleMouseOver(event) {
        const span = event.currentTarget.querySelector('span');
        span.style.color = getRandomAccentColor();
    }

    function handleMouseLeave(event) {
        const span = event.currentTarget.querySelector('span');
        span.style.color = '';
    }

    function handleLogout() {
        logout();
        navigate('/auth?mode=login');
    }

    return (
        <header className="sticky top-0 z-10 flex items-center justify-between gap-6 border-b border-border bg-background px-6 py-3">
            <div
                className="shrink-0 cursor-pointer font-heading text-lg font-semibold"
                onClick={goHome}
                onMouseOver={handleMouseOver}
                onMouseLeave={handleMouseLeave}
            >
                <span>Finance Dashboard</span>
            </div>

            <div className="max-w-md flex-1">
                <SearchBar />
            </div>

            <div className="flex shrink-0 items-center gap-2">
                {user
                    ? (
                        <>
                            <Button variant="ghost" aria-label="User" onClick={() => navigate(`/user/${user}`)}>{user}</Button>
                            <Button variant="outline" aria-label="logout" onClick={handleLogout}>Log Out</Button>
                        </>
                    )
                    : (
                        <Button type="button" onClick={() => navigate('/auth?mode=login')}>Log In</Button>
                    )}
            </div>
        </header>
    )
}