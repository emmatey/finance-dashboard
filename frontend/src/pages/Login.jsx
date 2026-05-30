import Header from '../components/Header.jsx'
import Footer from '../components/Footer.jsx'
import LogIn from '../components/LogIn.jsx';
import { useState } from "react"

export default function Login() {
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

