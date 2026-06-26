import ScreenersCard from "./ScreenersCard";
import useScreenersData from "./useScreenersData";

export default function ScreenersShard() {
    const { loading, data, error } = useScreenersData();

    if (loading) return <div>Loading...</div>;
    if (error) return <p>{error}</p>;

    return (
        <>
            {Object.entries(data ?? {}).map(([categoryName, itemsArray], idx) => (
                <ScreenersCard key={idx} title={categoryName} data={itemsArray} />
            ))}
        </>
    )
}
