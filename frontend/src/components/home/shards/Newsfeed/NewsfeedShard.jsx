import useNewsfeed from "./useNewsfeed";

export default function NewsfeedShard() {
    const { loading, data, error, responseCode } = useNewsfeed();

    return (
        <>
        </>
    )
}
