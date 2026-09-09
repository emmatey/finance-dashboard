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
    const [user, setUser] = useState(undefined)
    const [email, setEmail] = useState(undefined)
    const [verified, setVerified] = useState(undefined)

    async function refreshUser() {
        const res = await meRequest();
        if (res instanceof Error) {
            setUser(null)
            setEmail(null)
            setVerified(false)
            return
        }
        setUser(res?.username ?? null)
        setEmail(res?.email ?? null)
        setVerified(Boolean(res?.verified))
    }

    useEffect(() => {
        refreshUser();
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
        <AuthContext.Provider value={{ user, email, verified, setUser, setEmail, setVerified, logout, refreshUser }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)