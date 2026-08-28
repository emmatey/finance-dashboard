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
                    <CardHeader>
                        <CardTitle>
                            Change Your Password.
                        </CardTitle>
                        <CardDescription>
                            If you already have your account credentials, you can use this form to change your password.
                        </CardDescription>
                    </CardHeader>
                    <form onSubmit={(e) => (handleSubmit(e))}>
                        <CardContent>
                            <Field className="mb-5">
                                <FieldLabel htmlFor="currentPw"> Current Password </FieldLabel>
                                <Input
                                    required
                                    name="currentPw"
                                    id="currentPw"
                                    type="password"
                                />
                            </Field>

                            <Field>
                                <FieldLabel htmlFor="newPw1"> New Password </FieldLabel>
                                <Input
                                    required
                                    name="newPw1"
                                    id="newPw1"
                                    type="password"
                                    aria-invalid={!pwEqual}
                                    onChange={() => {
                                        setPwEqual(true)
                                        setFormErrorStr("")
                                    }}
                                />
                            </Field>

                            <Field>
                                <FieldLabel htmlFor="newPw2"> Confirm New Password</FieldLabel>
                                <Input
                                    required
                                    name="newPw2"
                                    id="newPw2"
                                    type="password"
                                    aria-invalid={!pwEqual}
                                    onChange={() => {
                                        setPwEqual(true)
                                        setFormErrorStr("")
                                    }}
                                />
                                <small className="text-destructive">{formErrorStr}</small>
                            </Field>
                        </CardContent>
                        <CardFooter>
                            <Button type="submit" variant="outline">
                                Submit
                            </Button>
                        </CardFooter>
                    </form>
                </>
            }

            {errorCode && !confirmed &&
                <>
                    <CardHeader>
                        <CardTitle>
                            Oops! There was a problem.
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="mb-3">Error Code: {errorCode}</p>
                        <p>{errorStr}</p>
                    </CardContent>
                    <CardFooter>
                        <Button variant="destructive" onClick={resetState}>
                            Back
                        </Button>
                    </CardFooter>
                </>
            }

            {confirmed && !errorCode &&
                <>
                    <CardHeader>
                        <CardTitle>
                            Success!
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p>{successStr}</p>
                    </CardContent>
                    <CardFooter>
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