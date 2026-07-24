import { useState } from "react"
import { useNavigate } from 'react-router-dom';
import { useAuth } from "../../context/AuthContext";
import { parseResponse } from "../../scripts/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

async function logIn(username, password) {
    const safeUsername = String(username).trim();
    const safePassword = String(password).trim();

    try {
        const response = await fetch('/api/auth/login', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: safeUsername,
                password: safePassword
            })
        });

        if (response.status === 401) {
            return false;
        }

        await parseResponse(response);
        return true;
    } catch (error) {
        console.error(error.message);
        return null;
    }
}

export default function Login({ onSetMode }) {
    const[username, setUsername] = useState("");
    const[password, setPassword] = useState("");
    const {setUser} = useAuth();
    // used to trigger elements which are in response to user entering incorrect login info.
    const[wrong, setWrong] = useState(false);
    const[loading, setLoading] = useState(false);
    const[serverError, setServerError] = useState(false);
    const navigate = useNavigate();

    async function handleLogIn() {
        setLoading(true);
        try {
            const status = await logIn(username, password);
            if (status === null) {
                setServerError(true);
            } else if (status === false) {
                setWrong(true);
            } else {
                setUser(username);
                navigate('/');
            }
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="flex justify-center px-6 py-16">
            <Card className="w-full max-w-sm">
                <CardHeader>
                    <CardTitle>Log in</CardTitle>
                </CardHeader>
                <CardContent>
                    <form className="flex flex-col gap-4" onSubmit={(e)=>{e.preventDefault(); handleLogIn()}}>
                        <div className="flex flex-col gap-2">
                            <Label htmlFor="username">Username</Label>
                            <Input
                                type="text"
                                id="username"
                                onChange={(e) => {setUsername(e.target.value); setWrong(false); setServerError(false);}}
                            />
                        </div>

                        <div className="flex flex-col gap-2">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="password">Password</Label>
                                {/* onSetMode is used to "navigate" see /pages/auth.jsx*/}
                                <button
                                    type="button"
                                    className="text-sm text-muted-foreground underline underline-offset-4 hover:text-foreground"
                                    onClick={() => onSetMode('change')}
                                >
                                    Forgot password?
                                </button>
                            </div>
                            <Input
                                type="password"
                                id="password"
                                onChange={(e) => {setPassword(e.target.value); setWrong(false); setServerError(false);}}
                            />
                        </div>

                        {wrong ? (
                            <p className="text-sm text-destructive">
                                Unknown username or password.{' '}
                                <button type="button" className="underline underline-offset-4" onClick={() => onSetMode('register')}>Register</button>
                                {' '}for a new account?
                            </p>
                        ) : null}

                        {serverError ? (
                            <p className="text-sm text-destructive">Unable to reach server. Please try again.</p>
                        ) : null}

                        <Button type="submit" disabled={loading}>{loading ? 'Logging in...' : 'Log In'}</Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}