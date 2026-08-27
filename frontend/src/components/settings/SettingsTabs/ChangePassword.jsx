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
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const currentPw = formData.get("currentPw");
        const pw1 = formData.get("newPw1");
        const pw2 = formData.get("newPw2");
        if (pw1 !== pw2) {
            setPwEqual(false);
            setFormErrorStr("Username and password provided are not equal.")
            return;
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
            return result;
        } catch (error) {
            setErrorStr(error.data);
            setErrorCode(error.status);
        }
    }

    async function handleSubmit(event) {
        event.preventDefault();
        const {currentPw, newPw} = checkPwFieldsEqual(event);
        console.log(currentPw)
        console.log(newPw)
        if (newPw) {
            const result = await submitPwChangeRequest(user, currentPw, newPw);
            console.log(result);
        } else {
            return;
        }
    }

    const state = getState(confirmed, errorCode);

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
                    <CardContent>
                        <form onSubmit={(e) => (handleSubmit(e))}>
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
                                <small className="text-destructive">{formErrorStr}</small>
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

                            <CardFooter>
                                <Button type="submit" variant="outline">
                                    Submit
                                </Button>
                            </CardFooter>
                        </form>
                    </CardContent>
                </>
            }

            {state === 'error' &&
                <>
                    <p>{errorCode}</p>
                    <p>{errorStr}</p>
                </>
            }

            {state === 'confirmed' &&
                <>
                    <p>{ }</p>
                </>
            }
        </Card>
    )
}