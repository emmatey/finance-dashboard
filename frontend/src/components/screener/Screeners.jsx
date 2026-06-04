import Header from "../Header";
import Footer from "../Footer";
import { parseResponse } from "../../scripts/utils";
import { useEffect, useState } from "react";

export default function Screeners({ subset }) {

    const [screenerData, setScreenerData] = useState([]);
    
    async function fetchScreenerData() {
        try {
            const response = await fetch("/api/screeners", {
                method: "GET"
            });
            const success = response['success'];
            console.log(success);


        } catch (error) {
            console.error(error.message);
            return null;
        };
    }

    useEffect(() => {
        (async () => {
            const data = await fetchScreenerData();
            setScreenerData(data);
        })();
    }, [subset]);

    console.log("SCREENER DATA STATE")
    console.log(typeof(screenerData));
    console.log(screenerData);

    return (
        <>
        <p> Screener! </p>

        </>
    )
}
