import { useState } from "react"
import { useNavigate } from 'react-router-dom';
import { logIn } from "../../scripts/backend-fetch";
import { useAuth } from "../../context/AuthContext";

export default function Login({ onSetMode }) {
    const[username, setUsername] = useState("");
    const[password, setPassword] = useState("");
    const {setUser} = useAuth();
    // used to trigger elements which are in response to user entering incorrect login info.
    const[wrong, setWrong] = useState(false);
    const[loading, setLoading] = useState(false);
    const[serverError, setServerError] = useState(false);
    const navigate = useNavigate();

    async function handleLogIn() {
        setLoading(true);
        try {
            const status = await logIn(username, password);
            if (status === null) {
                setServerError(true);
            } else if (status === false) {
                setWrong(true);
            } else {
                setUser(username);
                navigate('/');
            }
        } finally {
            setLoading(false);
        }
    }

    return (
        <>
        <div>
            <form onSubmit={(e)=>{e.preventDefault(); handleLogIn()}}>
                <h2>Log in!</h2>
                <label htmlFor="username"> Username </label>
                <input type="text" id="username" onChange={(e) => {setUsername(e.target.value); setWrong(false); setServerError(false);}}/>
                {/* onSetMode is used to "navigate" see /pages/auth.jsx*/}
                {wrong ? <small>Unknown username or password. <button type="button" onClick={() => onSetMode('change')}>Reset password?</button></small> : null}

                <label htmlFor="password"> Password </label>
                <input type="password" id="password" onChange={(e) => {setPassword(e.target.value); setWrong(false); setServerError(false);}}/>
                {wrong ? <small><button type="button" onClick={() => onSetMode('register')}>Register</button> for a new account?</small> : null}

                {serverError ? <small>Unable to reach server. Please try again.</small> : null}
                <button type="submit" disabled={loading}>{loading ? 'Logging in...' : 'Log In'}</button>
            </form>
        </div>
        </>
    )
}