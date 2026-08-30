import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { parseResponse } from "@/scripts/utils";
import { useState } from "react";
import { Spinner } from "@/components/ui/spinner";
import { useAuth } from "@/context/AuthContext";


export default function VerifyEmail() {
    /*
        This component is a form which allows users to verify their email.
        It should show the current verified email, and upon verification of a new email,
        drop the prior email from the account.
     */
    const [loading, setLoading] = useState(false);
    const [responseCode, setResponseCode] = useState(null);
    const [responseStr, setResponseStr] = useState("");
    const [error, setError] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const { email, verified } = useAuth();
    const [newEmail, setNewEmail] = useState("");

    function resetState() {
        setLoading(false);
        setResponseCode(null);
        setResponseStr("");
        setError(false);
        setSubmitted(false);
        setNewEmail("");
    }

    async function submitVerifyEmail(event) {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const submittedEmail = formData.get("email");
        setNewEmail(submittedEmail);
        try {
            setLoading(true);
            const response = await fetch("/api/auth/token/generate/verify_email", {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    "email": submittedEmail
                })
            });
            const result = await parseResponse(response);
            setResponseCode(result?.status);
            setResponseStr(result?.message);
        } catch (error) {
            setResponseCode(error?.status);
            setResponseStr(error?.message);
            setError(true);
        } finally {
            setLoading(false);
            setSubmitted(true);
        }
    }

    return (
        <Card className="w-full max-w-md border border-border/80 bg-card/95 shadow-lg shadow-primary/5 backdrop-blur-sm">
            {loading && (
                <>
                    <CardHeader className="space-y-2 pb-4">
                        <CardTitle className="text-2xl font-semibold tracking-tight">Sending verification</CardTitle>
                    </CardHeader>
                    <CardContent className="flex justify-center py-8">
                        <Spinner />
                    </CardContent>
                </>
            )}

            {!loading && !submitted && !error && (
                <>
                    <CardHeader className="space-y-2 pb-4">
                        <CardTitle className="text-2xl font-semibold tracking-tight">Verify your email</CardTitle>
                        <CardDescription className="text-sm text-muted-foreground">
                            Verify your email, or change the email associated with your account.
                        </CardDescription>
                    </CardHeader>
                    <form onSubmit={submitVerifyEmail}>
                        <CardContent className="space-y-4">
                            {email ? (
                                <div className="flex items-center gap-2">
                                    <p className="text-sm text-muted-foreground">
                                        Your email <span className="font-medium text-foreground">{email}</span> is currently
                                    </p>
                                    {verified ? (
                                        <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium uppercase tracking-[0.12em] text-emerald-600 dark:text-emerald-400">
                                            Verified
                                        </span>
                                    ) : (
                                        <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-0.5 text-xs font-medium uppercase tracking-[0.12em] text-amber-600 dark:text-amber-400">
                                            Not verified
                                        </span>
                                    )}
                                </div>
                            ) : (
                                <p className="text-sm text-muted-foreground">
                                    There isn't an email associated with this account currently.
                                </p>
                            )}

                            <div className="space-y-2">
                                <Label htmlFor="email" className="text-sm font-medium">Email address</Label>
                                <Input
                                    id="email"
                                    name="email"
                                    type="email"
                                    defaultValue={email}
                                    placeholder={email || "you@example.com"}
                                    required
                                    className="h-11 rounded-md border-border bg-background/80"
                                />
                            </div>
                        </CardContent>
                        <CardFooter>
                            <Button type="submit" className="w-full h-11">
                                Submit
                            </Button>
                        </CardFooter>
                    </form>
                </>
            )}

            {!loading && !error && submitted && (
                <>
                    <CardHeader className="space-y-2 pb-4">
                        <div className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.12em] text-emerald-600 dark:text-emerald-400 w-fit">
                            Sent
                        </div>
                        <CardTitle className="text-2xl font-semibold tracking-tight text-emerald-600 dark:text-emerald-400">
                            Check your inbox
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">
                            An email has been sent to <span className="font-medium text-foreground">{newEmail}</span>.
                        </p>
                    </CardContent>
                    <CardFooter>
                        <Button
                            className="w-full h-11 bg-emerald-600 text-white hover:bg-emerald-700"
                            onClick={resetState}
                        >
                            Done
                        </Button>
                    </CardFooter>
                </>
            )}

            {!loading && error && (
                <>
                    <CardHeader className="space-y-2 pb-4">
                        <CardTitle className="text-2xl font-semibold tracking-tight text-destructive">
                            Unable to send verification
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-col gap-4">
                        <div className="flex flex-col gap-2 p-3 bg-destructive/10 rounded-md border border-destructive/30">
                            <p className="text-sm font-medium text-destructive">Status code: {responseCode}</p>
                            <p className="text-sm text-destructive">{responseStr}</p>
                        </div>
                    </CardContent>
                    <CardFooter>
                        <Button onClick={resetState} variant="outline" className="w-full h-11">
                            Back
                        </Button>
                    </CardFooter>
                </>
            )}
        </Card>
    )
}