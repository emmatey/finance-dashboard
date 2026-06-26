import useUserSummary from "./useUserSummary";

export default function UserSummaryShard() {
    const { loading, data, error, responseCode } = useUserSummary();

    if (loading) return <div>Loading...</div>;
    if (error) return <p>{error}</p>;

    return (
        <div>
        </div>
    );
}
