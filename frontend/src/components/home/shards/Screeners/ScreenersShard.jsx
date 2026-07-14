import useScreenersData from "./useScreenersData";
import { useState } from "react";

export default function ScreenersShard() {
    const [categoryParam, setCategoryParam] = useState(null);
    const [screenerParam, setScreenerParam] = useState(null);
    const { availableLoading, dataLoading, errorMsg, screenersAvailable, screenerData } = useScreenersData(categoryParam, screenerParam);

    if (dataLoading) return <div>loading...</div>;
    if (errorMsg) return <p>{errorMsg}</p>;

    return (
        <>
        
        </>
    )
}
