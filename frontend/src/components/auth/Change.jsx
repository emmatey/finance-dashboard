import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { parseResponse } from "@/scripts/utils";
import { useState } from "react";
import { useSearchParams } from 'react-router-dom';

function getState(token, sent, errorCode, confirmed) {
    if (confirmed) return 'confirmed';
    if (sent) return 'sent';
    if (errorCode) return 'error';
    if (token) return 'reset';
    return 'request';
}

export default function Change() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const [sent, setSent] = useState(false);
    const [errorStr, setErrorStr] = useState(null);
    const [errorCode, setErrorCode] = useState(null);
    const [username, setUsername] = useState(null);
    const [email, setEmail] = useState(null);
    const [pwEqual, setPwEqual] = useState(true);
    const [confirmed, setConfirmed] = useState(false);
    const [newPw, setNewPw] = useState("");
    const [hideNewPw, setHideNewPw] = useState(true);

    const state = getState(token, sent, errorCode, confirmed);

    async function handleRequestPwReset(event) {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const email = formData.get("email");
        if (email) {
            try {
                const response = await fetch(`/api/auth/token/generate/forgot_pw?email=${encodeURIComponent(email)}`);
                const result = await parseResponse(response);
                setUsername(result.username);
                setSent(true);
            } catch (error) {
                if (error.status === 400) {
                    setSent(true);
                } else {
                    setErrorStr(error.data);
                    setErrorCode(error.status);
                };
            };
        } else {
            return;
        };
    }

    async function submitPwChange(token, pw) {
        try {
            const response = await fetch("/api/auth/token/verify/forgot_pw", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'token': token,
                    'new_password': pw
                })
            });
            const result = await parseResponse(response);
            setEmail(result.email);
            setUsername(result.username);
            setNewPw(pw);
            setConfirmed(true);
        } catch (error) {
            setErrorStr(error.data);
            setErrorCode(error.status);
        };
    }

    function checkPwFieldsEqual(event) {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const pw1 = formData.get("password1");
        const pw2 = formData.get("password2");
        if (pw1 !== pw2) {
            setPwEqual(false);
        } else {
            return pw1;
        }
    }

    function handleSubmitPwChange(event) {
        const pw = checkPwFieldsEqual(event);
        if (pw) {
            submitPwChange(token, pw);
        } else {
            return;
        }

    }
    return (
        <div className="flex justify-center px-6 py-16">
            <Card className="w-full max-w-sm">
                {state === 'request' && (
                    <>
                        <CardHeader>
                            <CardTitle>Change password</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <form onSubmit={handleRequestPwReset}>
                                <div className="flex flex-col gap-2 mb-2">
                                    <Label htmlFor="email-entry-field">Email</Label>
                                    <Input type="email" id="email-entry-field" name="email" placeholder="your_email@email.com" />
                                </div>
                                <Button type="submit">Submit</Button>
                            </form>
                        </CardContent>
                    </>
                )}

                {state === 'sent' && (
                    <CardContent className="flex flex-col items-center gap-4 py-8">
                        <p className="text-sm text-center">If that email exists, a password reset link has been sent.</p>
                        <Button onClick={() => window.location.replace("/auth")}>Go Back</Button>
                    </CardContent>
                )}

                {state === 'reset' && (
                    <>
                        <CardHeader>
                            <CardTitle>Hello {username}! Choose a new password</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <form onSubmit={(e) => handleSubmitPwChange(e)}>
                                <div className="flex flex-col gap-2 mb-2">
                                    <Label htmlFor="password1">New password</Label>
                                    <Input aria-invalid={pwEqual === false ? true : undefined} onChange={() => setPwEqual(true)} type="password" id="password1" name="password1" />
                                    <Label htmlFor="password2">Confirm password</Label>
                                    <Input aria-invalid={pwEqual === false ? true : undefined} onChange={() => setPwEqual(true)} type="password" id="password2" name="password2" />
                                </div>
                                <Button type="submit">Submit</Button>
                                <Button type="button" onClick={() => window.location.replace("/auth")}>Go Back</Button>
                            </form>
                        </CardContent>
                    </>
                )}

                {state === 'confirmed' && (
                    <>
                        <CardHeader>
                            <CardTitle>Success!</CardTitle>
                        </CardHeader>
                        <CardContent className="flex flex-col gap-2">
                            <p className="text-sm">You have changed the password for this account to:</p>
                            <p className="text-sm"><strong>Email:</strong> {email}</p>
                            <p className="text-sm"><strong>Username:</strong> {username}</p>
                            <div className="flex items-center gap-2">
                                <p className="text-sm"><strong>Password:</strong> {hideNewPw ? "•".repeat(newPw.length) : newPw}</p>
                                <Button type="button" onClick={() => setHideNewPw(!hideNewPw)}>{hideNewPw ? "Show" : "Hide"}</Button>
                            </div>
                            <Button onClick={() => window.location.replace("/auth")}>Go Back</Button>
                        </CardContent>
                    </>
                )}

                {state === 'error' && (
                    <>
                        <CardHeader>
                            <CardTitle>Oops wooks wike thewe was an ewwow... Code: {errorCode}</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-col gap-2 mb-2">
                                <p className="text-sm text-destructive">{errorStr}</p>
                            </div>
                            <Button onClick={() => window.location.replace("/auth")}>Go Back</Button>
                        </CardContent>
                    </>
                )}
            </Card>
        </div>
    );
}
