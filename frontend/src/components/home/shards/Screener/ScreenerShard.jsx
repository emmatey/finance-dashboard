import Header from "../../Header";
import Footer from "../../Footer";
import ScreenerCard from "./ScreenerCard";
import useScreenerData from "./useScreenerData";

export default function ScreenerShard() {
    const { loading, data, error } = useScreenerData();

    return (
        <>
        <p> Screener! </p>
        {error
            ? <p>{error}</p>
            : Object.entries(data ?? {}).map(([categoryName, itemsArray], idx) => {
                return <ScreenerCard key={idx} title={categoryName} data={itemsArray} />
            })
        }
        </>
    )
}
