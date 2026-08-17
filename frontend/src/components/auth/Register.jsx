import { useNavigate } from 'react-router-dom'
import { useState } from 'react';
import { useAuth } from "../../context/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function Register() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [password2, setPassword2] = useState("");
    const [passwordInvalidBorderCleared, setPasswordInvalidBorderCleared] = useState(true);
    const [email, setEmail] = useState("");
    const [errorStr, setErrorStr] = useState("");
    const { setUser } = useAuth();
    const navigate = useNavigate()

    async function handleRegister() {
        if (!comparePasswordFields()) {
            setPasswordInvalidBorderCleared(false);
            return;
        }
        const url = '/api/auth/register';
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: username.trim(),
                    password: password.trim(),
                    email: email.trim()
                })
            });

            const responseBody = await response.json();
            if (!responseBody['success']) {
                setErrorStr(responseBody?.message || 'Registration failed');
            } else {
                setUser(username.trim());
                navigate("/");
            }
        } catch (err) {
            console.error('Registration error:', err);
            setErrorStr('An error occurred while registering. Please try again.');
        }
    }

    function comparePasswordFields() {
        if (password !== password2){
            return false;
        } else {
            return true;
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
                            <Input
                                type="password"
                                id="password"
                                className={!passwordInvalidBorderCleared ? 'border-destructive' : ''}
                                onChange={(e) => {setPassword(e.target.value)}}
                                onFocus={() => (setPasswordInvalidBorderCleared(true))}
                            />
                        </div>

                        <div className="flex flex-col gap-2">
                            <Label htmlFor="confirmPassword">Confirm Password</Label>
                            <Input
                                type="password"
                                id="confirmPassword"
                                className={!passwordInvalidBorderCleared ? 'border-destructive' : ''}
                                onChange={(e) => {setPassword2(e.target.value)}}
                                onFocus={() => (setPasswordInvalidBorderCleared(true))}
                            />
                            {!passwordInvalidBorderCleared ? <p className="text-sm text-destructive">Passwords don't match</p> : null}
                        </div>

                        <div className="flex flex-col gap-2">
                            <Label htmlFor="email">Email (optional)</Label>
                            <Input type="email" id="email" onChange={(e) => {setEmail(e.target.value)}}/>
                        </div>

                        {errorStr ? <p className="text-sm text-destructive">{errorStr}</p> : null}

                        <Button type="submit">Register</Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}