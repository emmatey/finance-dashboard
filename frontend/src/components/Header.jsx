import { useNavigate } from 'react-router-dom'
import SearchBar from './SearchBar.jsx'
import '../styles/Header.css'

export default function Header() {
    const navigate = useNavigate()

    return (
        <header>
            <span className="header-logo" onClick={() => navigate('/home')}>
                Finance Dashboard
            </span>
            <div className="header-right">
                <SearchBar />
                <button className="header-user-btn" aria-label="User" />
            </div>
        </header>
    )
}
