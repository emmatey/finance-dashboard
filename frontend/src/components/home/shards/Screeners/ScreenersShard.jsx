import useScreenerData from "./useScreenerData";
import { useState } from "react";

export default function ScreenersShard() {
    const [categoryParam, setCategoryParam] = useState(null);
    const [screenerParam, setScreenerParam] = useState(null);
    const { dataLoading, errorMsg, screenerData } = useScreenerData(categoryParam, screenerParam);

    if (dataLoading) return <div>loading...</div>;
    if (errorMsg) return <p>{errorMsg}</p>;

    return (
        <>
        
        </>
    )
}
