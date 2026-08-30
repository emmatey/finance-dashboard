import { createContext, useContext, useEffect, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(undefined)  // undefined = still loading, null = not logged in
    const [email, setEmail] = useState(undefined)
    const [verified, setVerified] = useState(undefined)

    useEffect(() => {
        fetch('/api/session/me')
            .then(res => res.json())
            .then((data) => {
                setUser(data?.username ?? null)
                setEmail(data?.email ?? null)
                setVerified(Boolean(data?.verified ?? data?.validated ?? false))
            })
            .catch((error) => {
                console.error(error)
                setUser(null)
                setEmail(null)
                setVerified(false)
            })
    }, [])

    const logout = () => {
        fetch('/api/session/logout', { method: 'POST' })
            .finally(() => {
                setUser(null)
                setEmail(null)
                setVerified(false)
            })
    }

    return (
        <AuthContext.Provider value={{ user, email, verified, setUser, setEmail, setVerified, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
