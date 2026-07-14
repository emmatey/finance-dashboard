import { useEffect, useState } from "react";
import { parseResponse } from "@/scripts/utils";


export default function useAvailableScreeners() {
    const [availableLoading, setAvailableLoading] = useState(true);
    const [errorMsg, setErrMsg] = useState("");
    const [screenersAvailable, setScreenersAvailable] = useState([]);

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

    return { availableLoading, errorMsg, screenersAvailable }
}
