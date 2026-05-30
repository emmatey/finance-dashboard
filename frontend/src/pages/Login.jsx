import { useState } from "react"

export default function Login() {
    const[username, setUsername] = useState("emma");
    const[password, setPassword] = useState("123");

    async function login() {

        
        };
    return (
        <>
        <div>
        <form>
            <div>
                <input type="text"></input>
                <input type="text"></input>
                <button type='submit' onClick={login}>Log In!</button>
            </div>
        </form>
        </div>
        </>
    )
}

