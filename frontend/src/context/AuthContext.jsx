import { createContext, useContext, useEffect, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(undefined)  // undefined = still loading, null = not logged in
    const [email, setEmail] = useState(undefined);

    useEffect(() => {
        fetch('/api/session/me')
            .then(res => res.json())
            .then(data => setUser(data?.username ?? null))
            .then(data => setEmail(data?.email ?? null))
            .catch((error) => {
                console.error(error);
                setUser(null);
            })
    }, [])

    const logout = () => {
        fetch('/api/session/logout', { method: 'POST' })
            .finally(() => setUser(null))
    }

    return (
        <AuthContext.Provider value={{ user, email, setUser, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
