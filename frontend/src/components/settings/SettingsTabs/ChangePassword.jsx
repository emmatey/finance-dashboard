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


export default function ChangePassword(confirmed, error) {
    function getState() {
        if (confirmed) return 'confirmed';
        if (error) return 'error';
        return 'request';
    }

    function handleSubmit(event) {
        event.preventDefault();
        const pw = checkPwFieldsEqual(event);
        if (pw) {
            submitPwChangePostRequest(username, password, newPassword)
        } else {
            return;
        }
    }

    async function submitPwChangePostRequest(username, password, newPassword) {
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
        } catch (error) {
            setErrorStr(error.data);
            setErrorCode(error.status);
        }
    }

    function checkPwFieldsEqual(event) {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const pw1 = formData.get("newPw1");
        const pw2 = formData.get("newPw2");
        if (pw1 !== pw2) {
            setPwEqual(false);
        } else {
            return pw1;
        }
    }

    const [errorStr, setErrorStr] = useState(null);
    const [errorCode, setErrorCode] = useState(null);
    const [pwEqual, setPwEqual] = useState(true);
    const [confirmed, setConfirmed] = useState(false);
    const [newPw, setNewPw] = useState("");
    const [hideNewPw, setHideNewPw] = useState(true);

    const state = getState(confirmed, error);

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
                                <Input id="currentPw" />
                            </Field>

                            <Field>
                                <FieldLabel htmlFor="newPw1"> New Password </FieldLabel>
                                <Input
                                    id="newPw1"
                                    type="password"
                                    aria-invalid={pwEqual === false ? true : undefined}
                                    onChange={() => setPwEqual(true)}
                                />
                            </Field>

                            <Field>
                                <FieldLabel htmlFor="newPw2"> Confirm New Password</FieldLabel>
                                <Input
                                    id="newPw2"
                                    type="password"
                                    aria-invalid={pwEqual === false ? true : undefined}
                                    onChange={() => setPwEqual(true)}
                                />
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
                </>
            }

            {state === 'confirmed' &&
                <>
                </>
            }
        </Card>
    )
}