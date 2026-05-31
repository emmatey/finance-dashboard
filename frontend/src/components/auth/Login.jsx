import { useState } from "react"

import { logIn } from "../../scripts/backend-fetch";

export default function Login() {
    const[username, setUsername] = useState("");
    const[password, setPassword] = useState("");
    // used to trigger elements which are in response to user entering incorrect login info.
    const[wrong, setwrong] = useState(false);

    async function handleLogIn() {
        const status = await logIn(username, password);

        if (status == false) {
            setwrong(true)
        };
    }

    const forgotPwStr = "Your username and password combination is unknown.";
    const registerStr = "Register for a new account?";
    return (
        <>
        <div>
            <form>
                <h2>Log in!</h2>
                <label htmlFor="username"> Username </label>
                <input type="text" id="username" onChange={(e) => {setUsername(e.target.value)}}/>
                {wrong ? <small><link to='/auth&mode=change'>{forgotPwStr}</link></small> : null}

                <label htmlFor="password"> Password </label>
                <input type="password" id="password" onChange={(e) => {setPassword(e.target.value)}}/>
                {wrong ? <small><link to='/auth&mode=register'>{registerStr}</link></small> : null}

                <button type="button" onClick={handleLogIn}> Log In </button>
            </form>
        </div>
        </>
    )
}