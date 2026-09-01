import { useEffect, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { useNavigate } from "react-router-dom";
import {
    Card,
    CardAction,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"


export default function VerifyEmailConfirm() {
    /*
        This component will recieve the link from the email sent to users for verification.
        It will process the request, and inform users if the request worked.
        It will redirect home.
     */
    // Look for 'token' in query param
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const navigate = useNavigate();
    const [loading, setLoading] = useState();
    const [responseCode, setResponseCode] = useState();
    const [responseStr ,setResponseStr] = useState();
    const [success, setSuccess] = useState();
    const [error, setError] = useState();

    function resetState(){
        setLoading(false);
        setResponseCode(null);
        setResponseStr(null);
        setSuccess(false);
        setError(false);
    }

    async function handleVerifyToken(event) {
        try {
            setLoading(true);
            const response = await fetch("/api/auth/token/generate/verify_email", {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    "token": token
                })
            });
            const result = await response.json();
            setResponseCode(result?.status);
            setResponseStr(result?.message);
        } catch (error) {
            setResponseCode(error?.status);
            setResponseStr(error?.message);
            setError(true);
        } finally {
            setLoading(false);
            setSuccess(true);
        }
    }

    useEffect(() => {
        if (token) {
            handleVerifyToken();
        } else {
            navigate('/');
        }
        return resetState;
    }, [token, handleVerifyToken]);

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