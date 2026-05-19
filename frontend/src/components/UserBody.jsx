import { useEffect, useState } from 'react'
import { unpackFetchResponse } from '../scripts/utils.js'

export default function UserBody({ username }) {
    const [data, setData] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!username) return
        setData(null)
        setError(null)
        fetch(`/api/user/summary?username=${username}`)
            .then(unpackFetchResponse)
            .then(setData)
            .catch(err => setError(err.message))
    }, [username])

    if (!username) return <main><h2>User</h2><p>No user specified.</p></main>
    if (error) return <main><h2>User: {username}</h2><p>Error: {error}</p></main>
    if (!data) return <main><h2>User: {username}</h2><p>Loading...</p></main>

    return (
        <main>
            <h2>User: {username}</h2>
            <pre>{JSON.stringify(data, null, 2)}</pre>
        </main>
    )
}
