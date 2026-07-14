import useScreenersData from "./useScreenersData";

export default function ScreenersShard() {
    const { loading, errorMsg, screenersAvailable, screenerData } = useScreenersData();

    if (loading) return <div>Loading...</div>;
    if (errorMsg) return <p>{errorMsg}</p>;

    console.log(screenersAvailable);
    console.log(screenerData);
    return (
        <>

        </>
    )
}
