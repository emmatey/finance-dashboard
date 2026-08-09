import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { useSearchParams } from 'react-router-dom';
import { useState } from "react";

function getState(token, sent, error) {
    if (sent) return 'sent';
    if (error) return 'error';
    if (token) return 'reset';
    return 'request';
}

export default function Change() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const [sent, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const state = getState(token, sent, error);

    function handleRequestPw() {
        const request = new Request("/api/auth/generate/forgot_pw")
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
                            <div className="flex flex-col gap-2">
                                <Label htmlFor="email">Email</Label>
                                <Input type="email" id="email" placeholder="your_email@email.com" />
                            </div>
                            <Button>Submit</Button>
                        </CardContent>
                    </>
                )}

                {state === 'sent' && (
                    <CardContent className="flex justify-center py-8">
                        <Spinner className="size-6" />
                    </CardContent>
                )}

                {state === 'reset' && (
                    <>
                        <CardHeader>
                            <CardTitle>Choose a new password</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-col gap-2">
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
                            <p className="text-sm text-destructive">{error}</p>
                        </CardContent>
                    </>
                )}
            </Card>
        </div>
    );
}