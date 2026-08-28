import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { parseResponse } from "@/scripts/utils";
import { Spinner } from "../ui/spinner";
import { useState } from "react";
import { useSearchParams } from 'react-router-dom';

function getState(loading, token, sent, errorCode, confirmed) {
    if (loading) return 'loading';
    if (errorCode) return 'error';
    if (confirmed) return 'confirmed';
    if (sent) return 'sent';
    if (token) return 'reset';
    return 'request';
}

export default function ChangePwViaEmailToken() {
    /*
    Menu for changing password via emailed token "forgot pw"
     */
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const [sent, setSent] = useState(false);
    const [errorStr, setErrorStr] = useState(null);
    const [errorCode, setErrorCode] = useState(null);
    const [username, setUsername] = useState(null);
    const [email, setEmail] = useState(null);
    const [pwEqual, setPwEqual] = useState(true);
    const [confirmed, setConfirmed] = useState(false);
    const [loading, setLoading] = useState(false);

    const state = getState(loading, token, sent, errorCode, confirmed);

    async function handleRequestPwReset(event) {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const email = formData.get("email");
        if (email) {
            try {
                setLoading(true);
                const response = await fetch("/api/auth/token/generate/forgot_pw", {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 'email': email })
                });
                await parseResponse(response);
                setSent(true);
            } catch (error) {
                setErrorStr(error.message);
                setErrorCode(error.status);
            } finally {
                setLoading(false);
            };
        } else {
            return;
        };
    }

    async function submitPwChange(token, pw) {
        try {
            setLoading(true);
            const response = await fetch("/api/auth/token/verify/forgot_pw", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    'token': token,
                    'new_password': pw
                })
            });
            const result = await parseResponse(response);
            setEmail(result.email);
            setUsername(result.username);
            setConfirmed(true);
        } catch (error) {
            setErrorStr(error.message);
            setErrorCode(error.status);
        } finally {
            setLoading(false);
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
            <Card className="w-full max-w-md border border-border/80 bg-card/95 shadow-lg shadow-primary/5 backdrop-blur-sm">
                {state === 'loading' &&
                    <>
                        <CardHeader>
                            <CardTitle className="text-center text-xl">
                                Loading ...
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="flex justify-center py-8">
                            <Spinner />
                        </CardContent>
                    </>
                }
                {state === 'request' && (
                    <>
                        <CardHeader className="space-y-2 pb-4">
                            <CardTitle className="text-2xl font-semibold tracking-tight">Change password</CardTitle>
                            <p className="text-sm text-muted-foreground">Enter the email tied to your account and we’ll send a reset link.</p>
                        </CardHeader>
                        <CardContent>
                            <form onSubmit={handleRequestPwReset} className="space-y-4">
                                <div className="flex flex-col gap-2">
                                    <Label htmlFor="email-entry-field" className="text-sm font-medium">Email</Label>
                                    <Input className="h-11 rounded-md border-border bg-background/80" type="email" id="email-entry-field" name="email" placeholder="your_email@email.com" />
                                </div>
                                <Button type="submit" className="w-full h-11">Submit</Button>
                            </form>
                        </CardContent>
                    </>
                )}

                {state === 'sent' && (
                    <CardContent className="flex flex-col items-center gap-4 py-10 text-center">
                        <div className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.12em] text-emerald-600 dark:text-emerald-400">
                            Sent
                        </div>
                        <p className="text-sm text-muted-foreground max-w-xs">If that email exists, a password reset link has been sent.</p>
                        <Button className="w-full" onClick={() => window.location.replace("/auth")}>Go Back</Button>
                    </CardContent>
                )}

                {state === 'reset' && (
                    <>
                        <CardHeader className="space-y-2 pb-4">
                            <CardTitle className="text-2xl font-semibold tracking-tight">Choose a new password</CardTitle>
                            <p className="text-sm text-muted-foreground">Create a strong password you’ll remember.</p>
                        </CardHeader>
                        <CardContent>
                            <form onSubmit={(e) => handleSubmitPwChange(e)} className="space-y-4">
                                <div className="flex flex-col gap-3">
                                    <div className="space-y-2">
                                        <Label htmlFor="password1" className="text-sm font-medium">New password</Label>
                                        <Input className="h-11 rounded-md border-border bg-background/80" aria-invalid={pwEqual === false ? true : undefined} onChange={() => setPwEqual(true)} type="password" id="password1" name="password1" />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="password2" className="text-sm font-medium">Confirm password</Label>
                                        <Input className="h-11 rounded-md border-border bg-background/80" aria-invalid={pwEqual === false ? true : undefined} onChange={() => setPwEqual(true)} type="password" id="password2" name="password2" />
                                    </div>
                                    {pwEqual === false && (
                                        <p className="text-xs text-destructive">Passwords do not match.</p>
                                    )}
                                </div>
                                <div className="flex gap-2 pt-2">
                                    <Button
                                        type="button"
                                        onClick={() => window.location.replace("/auth")}
                                        variant="destructive"
                                        className="flex-1 h-11">
                                        Go Back
                                    </Button>
                                    <Button
                                        type="submit"
                                        className="flex-1 h-11">
                                        Submit
                                    </Button>
                                </div>
                            </form>
                        </CardContent>
                    </>
                )}

                {state === 'confirmed' && (
                    <>
                        <CardHeader className="space-y-2 pb-4">
                            <CardTitle className="text-2xl font-semibold tracking-tight text-emerald-600 dark:text-emerald-400">Success!</CardTitle>
                        </CardHeader>
                        <CardContent className="flex flex-col gap-3">
                            <p className="text-sm text-muted-foreground">You have successfully changed the password for this account:</p>
                            <div className="rounded-lg border border-border/80 bg-muted/40 p-3 space-y-2">
                                <p className="text-sm"><strong>Email:</strong> {email}</p>
                                <p className="text-sm"><strong>Username:</strong> {username}</p>
                            </div>
                            <Button className="w-full h-11" onClick={() => window.location.replace("/auth")}>Go Back</Button>
                        </CardContent>
                    </>
                )}

                {state === 'error' && (
                    <>
                        <CardHeader>
                            <CardTitle className="text-destructive">Error</CardTitle>
                        </CardHeader>
                        <CardContent className="flex flex-col gap-4">
                            <div className="flex flex-col gap-2 p-3 bg-destructive/10 rounded-md border border-destructive/30">
                                <p className="text-sm font-medium text-destructive">Status Code: {errorCode}</p>
                                <p className="text-sm text-destructive">{errorStr}</p>
                            </div>
                            <Button onClick={() => {
                                setErrorCode(null)
                                setErrorStr("")
                            }}
                                variant="outline">
                                Go Back
                            </Button>
                        </CardContent>
                    </>
                )}
            </Card>
        </div>
    );
}