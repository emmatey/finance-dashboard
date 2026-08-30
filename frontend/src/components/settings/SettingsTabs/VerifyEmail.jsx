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

    function resetState() {
        setLoading(false);
        setResponseCode(null);
        setResponseStr("");
        setError(false);
        setSubmitted(false);
    }

    async function submitVerifyEmail(email) {
        try {
            setLoading(true);
            const response = await fetch("/api/auth/token/generate/verify_email", {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    "email": email
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
        }
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>
                    Verify or Update Your email.
                </CardTitle>
                <CardDescription>
                    Verify your email, or change the email associated with your account.
                </CardDescription>
            </CardHeader>
            {!loading && !submitted &&
                <>
                    <CardContent>
                        {email &&
                            <p>
                                Your email {email} is currently {!verified && <strong>NOT</strong>} verified.
                            </p>
                        }
                        <form onSubmit={submitVerifyEmail}>
                            <Input
                                id="email"
                                name="email"
                                type="email"
                                defaultValue={email}
                                placeholder={email}
                            />
                        </form>
                        {!email && <small>There isn't an email associated with this account currently.</small>}
                    </CardContent>
                    <CardFooter>
                        <Button type="submit">
                            Submit
                        </Button>
                    </CardFooter>
                </>
            }

            {
                loading && !submitted &&
                <>
                    <CardContent>
                        <Spinner />
                    </CardContent>
                    <CardFooter>
                        <Button variant="destructive" onClick={resetState}>
                            Cancel
                        </Button>
                    </CardFooter>
                </>
            }

            {
                !loading && submitted &&
                <>
                    <CardContent>
                        Success!
                    </CardContent>
                    <CardFooter>
                        <Button onClick={() => (resetState)}>
                            Done
                        </Button>
                    </CardFooter>
                </>
            }
        </Card>
    )
}