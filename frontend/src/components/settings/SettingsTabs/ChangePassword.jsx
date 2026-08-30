import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { parseResponse } from "@/scripts/utils";
import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { Spinner } from "@/components/ui/spinner";


export default function ChangePassword() {
    const [errorStr, setErrorStr] = useState("");
    const [errorCode, setErrorCode] = useState(null);
    const [formErrorStr, setFormErrorStr] = useState("");
    const [pwEqual, setPwEqual] = useState(true);
    const [confirmed, setConfirmed] = useState(false);
    const [successStr, setSuccessStr] = useState("");
    const [loading, setLoading] = useState(false);
    const { user } = useAuth();

    function checkPwFieldsEqual(event) {
        const formData = new FormData(event.currentTarget);
        const currentPw = formData.get("currentPw");
        const pw1 = formData.get("newPw1");
        const pw2 = formData.get("newPw2");
        if (pw1 !== pw2) {
            setPwEqual(false);
            setFormErrorStr("Passwords do not match.")
            return {
                "currentPw": null,
                "newPw": null
            };
        } else {
            setPwEqual(true);
            return {
                "currentPw": currentPw,
                "newPw": pw1
            };
        }
    }

    async function submitPwChangeRequest(username, password, newPassword) {
        try {
            setLoading(true);
            const response = await fetch('/api/auth/change_pw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    'username': username,
                    'password': password,
                    'new_password': newPassword
                })
            })
            const result = await parseResponse(response);
            setConfirmed(true);
            setSuccessStr(result["message"])
        } catch (error) {
            setErrorStr(error.message);
            setErrorCode(error.status);
        } finally {
            setLoading(false);
        }
    }

    async function handleSubmit(event) {
        event.preventDefault();
        const { currentPw, newPw } = checkPwFieldsEqual(event);
        if (newPw) {
            await submitPwChangeRequest(user, currentPw, newPw);
        } else {
            return;
        }
    }

    function resetState() {
        setErrorCode(null);
        setErrorStr("");
        setFormErrorStr("");
        setPwEqual(true);
        setConfirmed(false);
        setSuccessStr("");
        setLoading(false);
    }

    return (
        <Card className="w-full max-w-md border border-border/80 bg-card/95 shadow-lg shadow-primary/5 backdrop-blur-sm">
            {loading && (
                <>
                    <CardHeader className="space-y-2 pb-4">
                        <CardTitle className="text-2xl font-semibold tracking-tight">Updating password</CardTitle>
                    </CardHeader>
                    <CardContent className="flex justify-center py-8">
                        <Spinner />
                    </CardContent>
                </>
            )}

            {!errorCode && !confirmed && !loading && (
                <>
                    <CardHeader className="space-y-2 pb-4">
                        <CardTitle className="text-2xl font-semibold tracking-tight">Change password</CardTitle>
                        <CardDescription className="text-sm text-muted-foreground">
                            Choose a new password for your account.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={(e) => handleSubmit(e)} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="currentPw" className="text-sm font-medium">Current password</Label>
                                <Input
                                    required
                                    name="currentPw"
                                    id="currentPw"
                                    type="password"
                                    placeholder="Enter your current password"
                                    className="h-11 rounded-md border-border bg-background/80"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="newPw1" className="text-sm font-medium">New password</Label>
                                <Input
                                    required
                                    name="newPw1"
                                    id="newPw1"
                                    type="password"
                                    placeholder="Create a new password"
                                    aria-invalid={pwEqual === false ? true : undefined}
                                    className="h-11 rounded-md border-border bg-background/80"
                                    onChange={() => {
                                        setPwEqual(true);
                                        setFormErrorStr("");
                                    }}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="newPw2" className="text-sm font-medium">Confirm new password</Label>
                                <Input
                                    required
                                    name="newPw2"
                                    id="newPw2"
                                    type="password"
                                    placeholder="Re-enter your new password"
                                    aria-invalid={pwEqual === false ? true : undefined}
                                    className="h-11 rounded-md border-border bg-background/80"
                                    onChange={() => {
                                        setPwEqual(true);
                                        setFormErrorStr("");
                                    }}
                                />
                                {formErrorStr && (
                                    <p className="text-xs text-destructive" role="alert">
                                        {formErrorStr}
                                    </p>
                                )}
                            </div>

                            <Button type="submit" className="w-full h-11">
                                Update password
                            </Button>
                        </form>
                    </CardContent>
                </>
            )}

            {errorCode && !confirmed && (
                <>
                    <CardHeader className="space-y-2 pb-4">
                        <CardTitle className="text-2xl font-semibold tracking-tight text-destructive">
                            Unable to update password
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-col gap-4">
                        <div className="flex flex-col gap-2 p-3 bg-destructive/10 rounded-md border border-destructive/30">
                            <p className="text-sm font-medium text-destructive">Status code: {errorCode}</p>
                            <p className="text-sm text-destructive">{errorStr}</p>
                        </div>
                        <Button onClick={resetState} variant="outline" className="w-full h-11">
                            Try again
                        </Button>
                    </CardContent>
                </>
            )}

            {confirmed && !errorCode && (
                <>
                    <CardHeader className="space-y-2 pb-4">
                        <div className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.12em] text-emerald-600 dark:text-emerald-400 w-fit">
                            Success
                        </div>
                        <CardTitle className="text-2xl font-semibold tracking-tight text-emerald-600 dark:text-emerald-400">
                            Password updated
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-col gap-4">
                        <p className="text-sm text-muted-foreground">{successStr}</p>
                        <Button
                            className="w-full h-11 bg-emerald-600 text-white hover:bg-emerald-700"
                            onClick={resetState}
                        >
                            Done
                        </Button>
                    </CardContent>
                </>
            )}
        </Card>
    )
}