import { useState } from "react";
import useNewsfeed from "./useNewsfeed";
import NewsStoryCard from "./NewsStoryCard";

export default function NewsfeedShard() {
    /*
        newsData: [{
            uuid: str,
            title: str,
            link: str,
            publisher: str,
            thumbnail: str,
            providerPublishTime: int
        }]
    */
   const [newsData, setNewsData] = useState(null);
   const { loading, data, error, responseCode } = useNewsfeed();
   if (loading) return <div>Loading...</div>;
   if (error) return <p>{`${error} ${responseCode}`}</p>;


    /* This component calls the use newsfeed hook and owns the state
    for that transaction. It also controls the visibility and lifecycle
    of the child NewsStoryCard components.
]
    It should contain the html for the card and the scrollable frame 
    that the news story cards sit within. 
    */
    return (
        <div>
        </div>
    );
}
