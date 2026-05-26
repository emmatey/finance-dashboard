import { useAuth } from "../context/AuthContext";

export default function Login() {
    const {user, login, logout} = useAuth();
    return (
        <>
        <p>Login!</p>
        <p>{user}</p>
        <button className='btn' onClick={login}></button>
        </>
        )
    }