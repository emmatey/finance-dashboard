import { createContext, useContext, useEffect, useState } from 'react'

const AuthContext = createContext(null)

async function meRequest() {
    try {
        const response = await fetch("/api/session/me", {
            method: "GET"
        });
        const res = await parseResponse(response);
        return res
    } catch (error) {
        return error
    }
}

export function AuthProvider({ children }) {
    const [user, setUser] = useState(undefined)  // undefined = still loading, null = not logged in
    const [email, setEmail] = useState(undefined)
    const [verified, setVerified] = useState(undefined)

    async function refreshUser(res) {
        setUser(res?.username);
        setEmail(res?.email);
        setVerified(res?.verified);
    }

    useEffect(async () => {
        const res = await meRequest();

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