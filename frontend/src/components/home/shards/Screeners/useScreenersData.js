import { useEffect, useState } from "react";
import { parseResponse } from "@/scripts/utils";


export default function useScreenersData(category = null, screener = null) {
    /*
        When called without parameters, should return the "available screeners list"
     */

    const [loading, setLoading] = useState(true);
    const [errorMsg, setErrMsg] = useState("");
    const [screenersAvailable, setScreenersAvailable] = useState(null);
    const [screenerData, setScreenerData] = useState(null);

    // Get available screeners on mount.
    useEffect(() => {
        async function fetchScreenersAvailable() {
            const response = await fetch('/api/screeners/available', {
                method: "GET"
            })
            const data = parseResponse(response);
            setScreenersAvailable(data);
        }
        fetchScreenersAvailable();
    }, []);

    // Get specific data on request.
    useEffect(() => {
        async function fetchScreenerData() {
            if (category) {
                url = `/api/screeners/?category=${String(category).trim()}`
            } else if (screener) {
                url = `/api/screeners/?screener=${String(category).trim()}`
            };
            const response = await fetch(url , {
                method: "GET"
            });
            const data = parseResponse(response);
            setScreenersAvailable(data);
        }
        fetchScreenersAvailable();
    }, [category, screener]);
}
