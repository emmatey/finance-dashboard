import { useEffect, useState } from "react";
import { parseResponse } from "@/scripts/utils";


export default function useNewsfeed() {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [responseCode, setResponseCode] = useState(null);

    useEffect(() => {
        async function fetchData() {
            try {
                const res = await fetch("/api/research/news?qty=100");
                const data = await parseResponse(res);
                setData(data?.data ?? null);
            } catch (err) {
                console.error(err);
                setResponseCode(err.status ?? null);
                if (err.status === 400) {
                    setError("Invalid request parameters.");
                } else if (err.status === 500) {
                    setError("Could not load news. Please try again later.");
                } else {
                    setError("An unexpected error occurred. Please try again.");
                }
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, []);

    return { loading, data, error, responseCode };
}
