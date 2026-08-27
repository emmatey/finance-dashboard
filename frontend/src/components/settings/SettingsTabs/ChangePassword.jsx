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


export default function ChangePassword() {
    const [errorStr, setErrorStr] = useState("");
    const [errorCode, setErrorCode] = useState(null);
    const [formErrorStr, setFormErrorStr] = useState("");
    const [pwEqual, setPwEqual] = useState(true);
    const [confirmed, setConfirmed] = useState(false);
    const [successStr, setSuccessStr] = useState("");
    const { user } = useAuth();

    function getState(confirmed, error) {
        if (confirmed) return 'confirmed';
        if (error) return 'error';
        return 'request';
    }

    function checkPwFieldsEqual(event) {
        const formData = new FormData(event.currentTarget);
        const currentPw = formData.get("currentPw");
        const pw1 = formData.get("newPw1");
        const pw2 = formData.get("newPw2");
        if (pw1 !== pw2) {
            setPwEqual(false);
            setFormErrorStr("Passwords do not match.")
            return {
                "currentPw": currentPw,
                "newPw": null
            };
        } else {
            return {
                "currentPw": currentPw,
                "newPw": pw1
            };
        }
    }

    async function submitPwChangeRequest(username, password, newPassword) {
        try {
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
        }
    }

    async function handleSubmit(event) {
        event.preventDefault();
        setErrorCode(null);
        setErrorStr("");
        const { currentPw, newPw } = checkPwFieldsEqual(event);
        if (newPw) {
            submitPwChangeRequest(user, currentPw, newPw);
        } else {
            return;
        }
    }

    const state = getState(confirmed, errorCode);
    console.warn(state);
    return (
        <Card>
            <CardHeader>
                <CardTitle>
                    Change Your Password.
                </CardTitle>
                <CardDescription>
                    If you already have your account credentials, you can use this form to change your password.
                </CardDescription>
            </CardHeader>

            {state === 'request' &&
                <>
                    <form onSubmit={(e) => (handleSubmit(e))}>
                        <CardContent>
                            <Field className="mb-5">
                                <FieldLabel> Current Password </FieldLabel>
                                <Input
                                    name="currentPw"
                                    type="password"
                                />
                            </Field>

                            <Field>
                                <FieldLabel htmlFor="newPw1"> New Password </FieldLabel>
                                <Input
                                    name="newPw1"
                                    type="password"
                                    aria-invalid={pwEqual === false ? true : undefined}
                                    onChange={() => {
                                        setPwEqual(true)
                                        setFormErrorStr("")
                                    }}
                                />
                            </Field>

                            <Field>
                                <FieldLabel htmlFor="newPw2"> Confirm New Password</FieldLabel>
                                <Input
                                    name="newPw2"
                                    type="password"
                                    aria-invalid={pwEqual === false ? true : undefined}
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

            {state === 'error' &&
                <CardContent>
                    <p>{errorCode}</p>
                    <p>{errorStr}</p>
                    <Button variant="destructive" onClick={() => {
                        setErrorStr("");
                        setErrorCode(null);
                    }}>
                        Back
                    </Button>
                </CardContent>
            }

            {state === 'confirmed' &&
                <CardContent>
                    <p>{successStr}</p>
                </CardContent>
            }
        </Card>
    )
}