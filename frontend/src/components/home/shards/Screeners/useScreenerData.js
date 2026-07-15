import { useEffect, useState } from "react";
import { parseResponse } from "@/scripts/utils";


export default function useScreenerData(screener = null, category = null) {
    const [dataLoading, setDataLoading] = useState(false);
    const [errorMsg, setErrMsg] = useState("");
    const [screenerData, setScreenerData] = useState(null);

    useEffect(() => {
        if (!category && !screener) return;
        async function fetchScreenerData() {
            try {
                setDataLoading(true);
                let url = null;
                if (category) {
                    url = `/api/screeners/fetch?category=${encodeURIComponent(String(category).trim())}`
                } else if (screener) {
                    url = `/api/screeners/fetch?screener=${encodeURIComponent(String(screener).trim())}`
                };
                if (url) {
                    const response = await fetch(url, {
                        method: "GET"
                    });
                    const data = await parseResponse(response);
                    setScreenerData(data["data"]);
                };
            } catch (error) {
                setErrMsg(error.message);
            } finally {
                setDataLoading(false);
            };
        }
        fetchScreenerData();
    }, [category, screener]);

    return { dataLoading, errorMsg, screenerData }
}
