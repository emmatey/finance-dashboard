import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { parseResponse } from "@/scripts/utils";
import { useState } from "react";
import { useSearchParams } from 'react-router-dom';

function getState(token, sent, error) {
    if (sent) return 'sent';
    if (error) return 'error';
    if (token) return 'reset';
    return 'request';
}

export default function Change() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const [sent, setSent] = useState(false);
    const [error, setError] = useState(null);

    const state = getState(token, sent, error);

    async function handleRequestPw(event) {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const email = formData.get("email");
        if (email) {
            try {
                const response = await fetch(`/api/auth/token/generate/forgot_pw?email=${email}`);
                const result = await parseResponse(response);
                setSent(true);
            } catch (error) {
                if (error.status == 400) {
                    setSent(true);
                } else {
                    setError(`${error.status} - ${error.data}`);
                };
            };
        } else {
            return;
        };
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
                            <form onSubmit={handleRequestPw}>
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
                            <CardTitle>Choose a new password</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-col gap-2 mb-2">
                                <Label htmlFor="password">New password</Label>
                                <Input type="password" id="password" />
                            </div>
                            <Button>Submit</Button>
                        </CardContent>
                    </>
                )}

                {state === 'error' && (
                    <>
                        <CardHeader>
                            <CardTitle>Something went wrong</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-col gap-2 mb-2">
                                <p className="text-sm text-destructive">{error}</p>
                            </div>
                            <Button onClick={() => window.location.replace("/auth")}>Go Back</Button>
                        </CardContent>
                    </>
                )}
            </Card>
        </div>
    );
}
