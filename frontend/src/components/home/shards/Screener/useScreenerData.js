import { useEffect, useState } from "react";
import { parseResponse } from "@/scripts/utils";


export default function useScreenerData() {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [responseCode, setResponseCode] = useState(null);

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const res = await fetch("/api/screeners");
                const data = await parseResponse(res);
                setData(data);
            } catch (err) {
                console.error(err);
                setResponseCode(err.status ?? null);
                if (err.status === 500) {
                    setError("Could not load screener data. Please try again later.");
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
