import useScreenersData from "./useScreenersData";
import { useState } from "react";

export default function ScreenersShard() {
    const [categoryParam, setCategoryParam] = useState(null);
    const [screenerParam, setScreenerParam] = useState(null);
    const { loading, errorMsg, screenersAvailable, screenerData } = useScreenersData(categoryParam, screenerParam);

    if (loading) return <div>Loading...</div>;
    if (errorMsg) return <p>{errorMsg}</p>;

    console.log(screenersAvailable);
    console.log(screenerData);
    return (
        <>

        </>
    )
}
