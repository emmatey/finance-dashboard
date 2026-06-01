import { useState, useEffect } from "react"
import { Link, useSearchParams } from 'react-router-dom';

import Change from "../components/auth/Change.jsx"
import Login from "../components/auth/Login.jsx"
import Register from "../components/auth/Register.jsx";


export default function Auth() {
    const validModes = ['login', 'change', 'register'];
    const [searchParams] = useSearchParams();
    const searchParamMode = searchParams.get("mode");
    const initialState = validModes.includes(searchParamMode) ? searchParamMode : 'login';

    const [mode, setMode] = useState(initialState);
    


    return (
        <>
        {mode === 'login' ? <Login onSetMode={setMode}/> : null}

        {mode === 'change' ? <Change onSetMode={setMode}/> : null}

        {mode === 'register' ? <Register onSetMode={setMode}/> : null}
        </>
    )
}

