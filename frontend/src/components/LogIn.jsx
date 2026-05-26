import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import Header from './Header.jsx'
import Footer from './Footer.jsx'

export default function LogIn() {
    async function handleLogIn(username, password) {
        const response = await fetch(
            URL="/api/auth/login", {
                method:"POST",
                body: {username: username, password: password}
            }
        );

        if(!response.ok) {
            console.error([response.status, response.statusText]);
            throw new Error(`Return code ${response.status}`);
        } else {
            // Parse response
            console.log(response.json())

        };
        
        // If login valid
            // Redirect to homepage
        // Oterwise show banner in red.
        


    return (
        <>
        <p>Login page here</p>
        </>
        )
    }
}
