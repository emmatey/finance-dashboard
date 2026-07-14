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

    if (!category && !screener) {
        async function getScreenersAvailable() {
            const response = await fetch('/api/screeners/available', {
                method: "GET"
            })
            const data = parseResponse(response);
            setScreenersAvailable(data);
        }
        useEffect(() => {
            getScreenersAvailable();
        }, []);
        
        return { loading, errorMsg, screenersAvailable, screenerData }
    };
}