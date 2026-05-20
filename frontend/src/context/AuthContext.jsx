import { createContext, useContext, useEffect, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(undefined)  // undefined = still loading, null = not logged in

    useEffect(() => {
        fetch('/api/auth/me')
            .then(res => res.ok ? res.json() : null)
            .then(data => setUser(data ? data.username : null))
            .catch(() => setUser(null))
    }, [])

    const login = (username) => setUser(username)
    const logout = () => {
        fetch('/api/auth/logout', { method: 'POST' })
            .finally(() => setUser(null))
    }

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
