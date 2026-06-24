import Header from "../../Header";
import Footer from "../../Footer";
import ScreenersCard from "./ScreenersCard";
import useScreenersData from "./useScreenersData";

export default function ScreenersShard() {
    const { loading, data, error } = useScreenersData();

    return (
        <>
        <p> Screener! </p>
        {error
            ? <p>{error}</p>
            : Object.entries(data ?? {}).map(([categoryName, itemsArray], idx) => {
                return <ScreenersCard key={idx} title={categoryName} data={itemsArray} />
            })
        }
        </>
    )
}
