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
import {
    Field,
    FieldLabel
} from "@/components/ui/field"
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
            setErrorStr(error.data);
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
        <Card>
            {loading &&
                <>
                    <CardHeader>
                        <CardTitle>
                            Loading...
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Spinner />
                    </CardContent>
                </>
            }

            {!errorCode && !confirmed && !loading &&
                <>
                    <CardHeader className="space-y-2 border-b bg-muted/20">
                        <CardTitle className="text-xl">Change your password</CardTitle>
                        <CardDescription className="max-w-2xl leading-relaxed">
                            If you already have your account credentials, you can use this form to change your password.
                        </CardDescription>
                    </CardHeader>
                    <form onSubmit={(e) => (handleSubmit(e))}>
                        <CardContent className="space-y-6 pt-6">
                            <Field className="space-y-2">
                                <FieldLabel htmlFor="currentPw">Current password</FieldLabel>
                                <Input
                                    required
                                    name="currentPw"
                                    id="currentPw"
                                    type="password"
                                    placeholder="Enter your current password"
                                    className="h-11"
                                />
                            </Field>

                            <Field className="space-y-2">
                                <FieldLabel htmlFor="newPw1">New password</FieldLabel>
                                <Input
                                    required
                                    name="newPw1"
                                    id="newPw1"
                                    type="password"
                                    placeholder="Enter a new password"
                                    aria-invalid={!pwEqual}
                                    className="h-11"
                                    onChange={() => {
                                        setPwEqual(true)
                                        setFormErrorStr("")
                                    }}
                                />
                            </Field>

                            <Field className="space-y-2">
                                <FieldLabel htmlFor="newPw2">Confirm new password</FieldLabel>
                                <Input
                                    required
                                    name="newPw2"
                                    id="newPw2"
                                    type="password"
                                    placeholder="Re-enter your new password"
                                    aria-invalid={!pwEqual}
                                    className="h-11"
                                    onChange={() => {
                                        setPwEqual(true)
                                        setFormErrorStr("")
                                    }}
                                />
                                {formErrorStr && (
                                    <small className="text-sm font-medium text-destructive" role="alert">
                                        {formErrorStr}
                                    </small>
                                )}
                            </Field>
                        </CardContent>
                        <CardFooter className="justify-end border-t bg-muted/10 pt-4">
                            <Button type="submit" className="min-w-28">
                                Update password
                            </Button>
                        </CardFooter>
                    </form>
                </>
            }

            {errorCode && !confirmed &&
                <>
                    <CardHeader className="border-b bg-destructive/5">
                        <CardTitle className="text-xl text-destructive">Unable to update password</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 pt-6">
                        <p className="text-sm font-medium">Error code: {errorCode}</p>
                        <p className="text-sm text-muted-foreground">{errorStr}</p>
                    </CardContent>
                    <CardFooter className="justify-end border-t pt-4">
                        <Button variant="destructive" onClick={resetState}>
                            Try again
                        </Button>
                    </CardFooter>
                </>
            }

            {confirmed && !errorCode &&
                <>
                    <CardHeader className="border-b bg-gain/5">
                        <CardTitle className="text-xl text-gain">Password updated</CardTitle>
                    </CardHeader>
                    <CardContent className="pt-6">
                        <p className="text-sm leading-relaxed text-muted-foreground">{successStr}</p>
                    </CardContent>
                    <CardFooter className="justify-end border-t pt-4">
                        <Button
                            className="bg-gain text-primary-foreground border border-transparent hover:border-border hover:bg-gain/80"
                            onClick={resetState}
                        >
                            Done
                        </Button>
                    </CardFooter>
                </>
            }
        </Card>
    )
}