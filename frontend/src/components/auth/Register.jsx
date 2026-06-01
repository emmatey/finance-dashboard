import Header from '../Header.jsx'
import Footer from '../Footer.jsx'
import { useState } from 'react';

export default function Register({ onSetMode }) {
    const [statusCode, setStatusCode] = useState(null);
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const statusCodeMap = {
        400: <small>Invalid username or password. add json body here? bla bla</small>,
        409: <small>Username in use already</small>
    };

    async function handleRegister() {
        const safeUsername = String(username).trim();
        const safePassword = String(password).trim();
        const url = '/api/auth/register';

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body:JSON.stringify({
                    username: safeUsername,
                    password: safePassword
                })
            });

            const responseBody = await response.json();
            console.log(responseBody);
            console.log(response.statusCode);
            

        } catch (error) {
            console.error(error.message);
            return(false);
        }
    }

    return (
        <>
        <div>
            <form>
                <h2>Register</h2>
                <label htmlFor="username"> Username </label>
                <input type="text" id="username" onChange={(e) => {setUsername(e.target.value)}}/>
                {statusCodeMap[statusCode] ? statusCodeMap[statusCode] : null}

                <label htmlFor="password"> Password </label>
                <input type="password" id="password" onChange={(e) => {setPassword(e.target.value)}}/>
                {statusCodeMap[statusCode] ? statusCodeMap[statusCode] : null}

                <button type="button" onClick={handleRegister}> Register </button>
            </form>
        </div>
        </>
    )
}
