import useScoreboard from "./useScoreboard";
import ScoreboardTable from "./ScoreboardTable";
import TableSkeleton from "@/components/TableSkeleton";

export default function ScoreboardShard() {
    const { loading, data, error, responseCode } = useScoreboard();

    if (loading) return <TableSkeleton />;
    if (error) return <p>{error}</p>;

    return (
        <>
            {
                data && Object.keys(data).length > 0 &&
                <ScoreboardTable data={data} />
            }
        </>
    );
}
