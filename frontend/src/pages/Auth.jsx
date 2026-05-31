import { useState, useEffect } from "react"
import { Link } from 'react-router-dom';

import Change from "../components/auth/Change.jsx"
import Login from "../components/auth/Login.jsx"
import Register from "../components/auth/Register.jsx";


export default function Auth() {
    const [mode, setMode] = useState('login');

    return (
        <>
        {mode === 'login' ? <Login onSetMode={setMode}/> : null}

        {mode === 'change' ? <Change onSetMode={setMode}/> : null}

        {mode === 'register' ? <Register onSetMode={setMode}/> : null}
        </>
    )
}

