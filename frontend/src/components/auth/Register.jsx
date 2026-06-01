import Header from '../Header.jsx'
import Footer from '../Footer.jsx'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react';

export default function Register({ onSetMode }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errorStr, setErrorStr] = useState("");
    const navigate = useNavigate()

    async function handleRegister() {
        const url = '/api/auth/register';
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: username.trim(),
                    password: password.trim()
                })
            });

            const responseBody = await response.json();
            if (!responseBody['success']) {
                setErrorStr(responseBody?.message || 'Registration failed');
            } else {
                navigate("/");
            }
        } catch (err) {
            console.error('Registration error:', err);
            setErrorStr('An error occurred while registering. Please try again.');
        }
    }

    return (
        <>
        <div>
            <form onSubmit={(e) => e.preventDefault}>
                <h2>Register</h2>
                <label htmlFor="username"> Username </label>
                <input type="text" id="username" onChange={(e) => {setUsername(e.target.value)}}/>

                <label htmlFor="password"> Password </label>
                <input type="password" id="password" onChange={(e) => {setPassword(e.target.value)}}/>
                {errorStr || null}

                <button type="submit" onClick={handleRegister}> Register </button>
            </form>
        </div>
        </>
    )
}