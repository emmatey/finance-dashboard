import { useEffect, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { useNavigate } from "react-router-dom";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"

async function verifyToken(token) {
    try {
        const response = await fetch("/api/auth/token/verify/verify_email", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                "token": token
            })
        });
        const result = await response.json();
        return result;

    } catch (error) {
        return (error)
    }
}

export default function VerifyEmailConfirm() {
    /*
        This component will receive a link from the email sent to users for email verification.
        It will process the request, and inform users if the request worked.
     */
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const navigate = useNavigate();

    const [loading, setLoading] = useState();
    const [responseCode, setResponseCode] = useState();
    const [responseStr, setResponseStr] = useState();
    const [success, setSuccess] = useState();
    const [error, setError] = useState();

    function resetState() {
        setLoading(false);
        setResponseCode(null);
        setResponseStr(null);
        setSuccess(false);
        setError(false);
    }

    useEffect(() => {
        async function handleVerifyToken(token) {
            const res = verifyToken(token);
            if (res instanceof Error) {
                setError(true);
            } else {
                setSuccess(true);
            };
            setResponseCode(res.status);
            setResponseStr(res.message);
        };

        if (token) {
            setLoading(true);
            handleVerifyToken(token);
            setLoading(false);
        } else {
            navigate('/');
        }
        return resetState;
    }, [token]);

    return (
        <>
            {loading && !success && !error &&
                <>
                    <Card>
                        <CardHeader>
                            <CardTitle>Verifying Email</CardTitle>
                            <CardDescription>Please wait while we verify your email address...</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p>Processing your verification request...</p>
                        </CardContent>
                    </Card>
                </>
            }

            {success && !error &&
                <>
                    <Card>
                        <CardHeader>
                            <CardTitle>Email Verified</CardTitle>
                            <CardDescription>Success</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p>{responseStr}</p>
                        </CardContent>
                        <CardFooter>
                            <p>Response Code: {responseCode}</p>
                        </CardFooter>
                    </Card>
                </>
            }

            {error &&
                <>
                    <Card>
                        <CardHeader>
                            <CardTitle>Verification Failed</CardTitle>
                            <CardDescription>Error</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p>{responseStr}</p>
                        </CardContent>
                        <CardFooter>
                            <p>Response Code: {responseCode}</p>
                        </CardFooter>
                    </Card>
                </>
            }
        </>
    )
}