import useScoreboard from "./useScoreboard";

export default function ScoreboardShard() {
    const { loading, data, error, responseCode } = useScoreboard();

    if (loading) return <div>Loading...</div>;
    if (error) return <p>{error}</p>;

    return (
        <div>
        </div>
    );
}
