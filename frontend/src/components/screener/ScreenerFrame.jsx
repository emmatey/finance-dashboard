import Header from "../Header";
import Footer from "../Footer";
import ScreenerCard from "./ScreenerCard";
import { parseResponse } from "../../scripts/utils";
import { useEffect, useState } from "react";

export default function ScreenerFrame() {
    const [screenerData, setScreenerData] = useState({});

    async function fetchScreenerData() {
        try {
            const response = await fetch("/api/screeners", {
                method: "GET"
            });
            const screenerJson = await parseResponse(response);
            return screenerJson;
        } catch (error) {
            console.error(error.message);
            return {};
        };
    }

    useEffect(() => {
        (async () => {
            const data = await fetchScreenerData();
            setScreenerData(data);
        })();
    }, []);

    return (
        <>
        <p> Screener! </p>
        {Object.entries(screenerData).map(([categoryName, itemsArray], idx) => {
            return <ScreenerCard key={idx} title={categoryName} data={itemsArray} />
        })}
        </>
    )
}
