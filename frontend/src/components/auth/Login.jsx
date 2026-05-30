import { useState } from "react"

import { logIn } from "../../scripts/backend-fetch";

export default function Login() {
    const[username, setUsername] = useState("");
    const[password, setPassword] = useState("");

    async function handleLogIn() {
        const status = await logIn(username, password);

        console.log(status);
    }
    return (
        <>
        <div>
            <form>
                <h2>Log in!</h2>
                <label htmlFor="username"> Username </label>
                <input type="text" id="username" onChange={(e) => {setUsername(e.target.value)}}/>

                <label htmlFor="password"> Password </label>
                <input type="password" id="password" onChange={(e) => {setPassword(e.target.value)}}/>

                <button type="button" onClick={handleLogIn}> Log In </button>
            </form>
        </div>
        </>
    )
}