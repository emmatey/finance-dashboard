import { createContext, useContext, useEffect, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(undefined)  // undefined = still loading, null = not logged in

    useEffect(() => {
        fetch('/api/auth/me')
            .then(res => res.json())
            .then(data => setUser(data?.username ?? null))
            .catch((error) => {
                console.error(error);
                setUser(null);
            })
    }, [])

    const logout = () => {
        fetch('/api/auth/logout', { method: 'POST' })
            .finally(() => setUser(null))
    }

    return (
        <AuthContext.Provider value={{ user, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
