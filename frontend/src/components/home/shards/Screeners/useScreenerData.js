import { useEffect, useState } from "react";
import { parseResponse } from "@/scripts/utils";

export default function useScreenerData(screeners = [], category = null) {
    const [dataLoading, setDataLoading] = useState(false);
    const [errorMsg, setErrMsg] = useState("");
    const [screenerData, setScreenerData] = useState(null);

    const screenersKey = screeners.join(",");

    useEffect(() => {
        if (!category && screeners.length === 0) return;

        const params = new URLSearchParams();
        if (category) {
            params.set("category", String(category).trim());
        } else {
            for (const screener of screeners) {
                params.append("screener", String(screener).trim());
            }
        }
        const url = `/api/screeners/fetch?${params.toString()}`;

        async function fetchScreenerData() {
            try {
                setDataLoading(true);
                const response = await fetch(url, {
                    method: "GET"
                });
                const data = await parseResponse(response);
                setScreenerData(data["data"]);
            } catch (error) {
                setErrMsg(error.message);
            } finally {
                setDataLoading(false);
            };
        }
        fetchScreenerData();
    }, [category, screenersKey]);

    return { dataLoading, errorMsg, screenerData }
}
