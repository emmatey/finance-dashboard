import { useEffect, useState } from "react";
import { parseResponse } from "@/scripts/utils";


export default function useScreenersData(category = null, screener = null) {
    /*
        When called without parameters, should return the "available screeners list"
     */

    const [availableLoading, setAvailableLoading] = useState(true);
    const [dataLoading, setDataLoading] = useState(false);
    const [errorMsg, setErrMsg] = useState("");
    const [screenersAvailable, setScreenersAvailable] = useState(null);
    const [screenerData, setScreenerData] = useState(null);

    // Get available screeners on mount.
    useEffect(() => {
        async function fetchScreenersAvailable() {
            try {
                const response = await fetch('/api/screeners/available', {
                    method: "GET"
                })
                const data = await parseResponse(response);
                setScreenersAvailable(data["data"]);
            } catch (error) {
                setErrMsg(error.message);
            } finally {
                setAvailableLoading(false);
            };
        }
        fetchScreenersAvailable();
    }, []);

    // Get specific data on request.
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

    return { availableLoading, dataLoading, errorMsg, screenersAvailable, screenerData }
}
