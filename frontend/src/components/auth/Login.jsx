import { useState } from "react"
import { useNavigate } from 'react-router-dom';
import { logIn } from "../../scripts/backend-fetch";

export default function Login({ onSetMode }) {
    const[username, setUsername] = useState("");
    const[password, setPassword] = useState("");
    // used to trigger elements which are in response to user entering incorrect login info.
    const[wrong, setWrong] = useState(undefined);
    const navigate = useNavigate();

    async function handleLogIn() {
        const status = await logIn(username, password);

        if (status === false) {
            setWrong(true)
        } else if (status === true) {
            navigate('/')
        }
    }

    return (
        <>
        <div>
            <form onSubmit={(e)=>{e.preventDefault(); handleLogIn()}}>
                <h2>Log in!</h2>
                <label htmlFor="username"> Username </label>
                <input type="text" id="username" onChange={(e) => {setUsername(e.target.value); setWrong(false);}}/>
                {/* onSetMode is used to "navigate" see /pages/auth.jsx*/}
                {wrong ? <small>Unknown username or password. <button type="button" onClick={() => onSetMode('change')}>Reset password?</button></small> : null}

                <label htmlFor="password"> Password </label>
                <input type="password" id="password" onChange={(e) => {setPassword(e.target.value); setWrong(false);}}/>
                {wrong ? <small><button type="button" onClick={() => onSetMode('register')}>Register</button> for a new account?</small> : null}

                <button type="submit"> Log In </button>
            </form>
        </div>
        </>
    )
}