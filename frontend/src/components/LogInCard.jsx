import { useState } from "react"

export default function LogInCard() {
    const[username, setUsername] = useState("emma");
    const[password, setPassword] = useState("123");

    async function login() {
        };
    return (
        <>
        <div className="card">
        <form>
            <div className="input-group">
                <input type="text" className="form-control"></input>
                <input type="text" className="form-control"></input>
                <button type='submit' className="btn-primary" onClick={login}>Log In!</button>
            </div>
        </form>
        </div>
        </>
        )
    }