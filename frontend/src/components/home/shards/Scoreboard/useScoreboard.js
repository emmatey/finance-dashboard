import { useEffect, useState } from "react";
import { parseResponse } from "@/scripts/utils";


export default function useScoreboard() {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState([]);
    const [error, setError] = useState("");
    const [responseCode, setResponseCode] = useState(null);

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const res = await fetch("/api/scoreboard");
                const data = await parseResponse(res);
                setData(data?.data);
            } catch (err) {
                console.error(err.message, err.data);
                setResponseCode(err.status ?? null);
                if (err.status === 500) {
                    setError("Could not load scoreboard. Please try again later.");
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
