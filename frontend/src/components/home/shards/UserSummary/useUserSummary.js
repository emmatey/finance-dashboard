import { useEffect, useState } from "react";
import { parseResponse } from "@/scripts/utils";


export default function useUserSummary(username) {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [responseCode, setResponseCode] = useState(null);

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const url = username
                    ? `/api/user/summary?username=${encodeURIComponent(username)}`
                    : '/api/user/summary';
                const res = await fetch(url);
                const data = await parseResponse(res);
                setData(data);
            } catch (err) {
                console.error(err);
                setResponseCode(err.status ?? null);
                if (err.status === 400) {
                    setError("No user session found. Please log in.");
                } else if (err.status === 404) {
                    setError("User not found.");
                } else if (err.status === 500) {
                    setError("Could not load user data. Some information may be missing.");
                } else {
                    setError("An unexpected error occurred. Please try again.");
                }
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [username]);

    return { loading, data, error, responseCode };
}