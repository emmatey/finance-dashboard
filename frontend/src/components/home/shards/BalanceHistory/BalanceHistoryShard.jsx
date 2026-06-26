import useBalanceHistory from "./useBalanceHistory";

export default function BalanceHistoryShard() {
    const { loading, data, error, responseCode } = useBalanceHistory();

    if (loading) return <div>Loading...</div>;
    if (error) return <p>{error}</p>;

    return (
        <div>
        </div>
    );
}
