import useNewsfeed from "./useNewsfeed";

export default function NewsfeedShard() {
    const { loading, data, error, responseCode } = useNewsfeed();

    if (loading) return <div>Loading...</div>;
    if (error) return <p>{error}</p>;

    return (
        <div>
        </div>
    );
}
