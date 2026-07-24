import Header from '@/components/Header.jsx'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function Register({ onSetMode }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errorStr, setErrorStr] = useState("");
    const navigate = useNavigate()

    async function handleRegister() {
        const url = '/api/auth/register';
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: username.trim(),
                    password: password.trim()
                })
            });

            const responseBody = await response.json();
            if (!responseBody['success']) {
                setErrorStr(responseBody?.message || 'Registration failed');
            } else {
                navigate("/");
            }
        } catch (err) {
            console.error('Registration error:', err);
            setErrorStr('An error occurred while registering. Please try again.');
        }
    }

    return (
        <div className="flex justify-center px-6 py-16">
            <Card className="w-full max-w-sm">
                <CardHeader>
                    <CardTitle>Register</CardTitle>
                </CardHeader>
                <CardContent>
                    <form className="flex flex-col gap-4" onSubmit={(e) => {e.preventDefault(); handleRegister();}}>
                        <div className="flex flex-col gap-2">
                            <Label htmlFor="username">Username</Label>
                            <Input type="text" id="username" onChange={(e) => {setUsername(e.target.value)}}/>
                        </div>

                        <div className="flex flex-col gap-2">
                            <Label htmlFor="password">Password</Label>
                            <Input type="password" id="password" onChange={(e) => {setPassword(e.target.value)}}/>
                        </div>

                        {errorStr ? <p className="text-sm text-destructive">{errorStr}</p> : null}

                        <Button type="submit">Register</Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}