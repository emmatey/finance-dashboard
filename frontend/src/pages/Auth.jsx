import { Outlet } from 'react-router-dom';

import Header from "../components/header/Header.jsx";


export default function Auth() {
    return (
        <>
        <Header />
        <Outlet />
        </>
    )
}