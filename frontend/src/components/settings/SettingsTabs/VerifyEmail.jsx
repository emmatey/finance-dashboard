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
    const { email } = useAuth();

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

        } finally {
            setLoading(false);
        }
    }


    return (
        <Card>
            {
                <>
                    <CardHeader>
                        <CardTitle>

                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <form>
                            <Input />
                        </form>
                    </CardContent>
                    <CardFooter>
                        <Button>

                        </Button>
                    </CardFooter>
                </>
            }
        </Card>
    )
}