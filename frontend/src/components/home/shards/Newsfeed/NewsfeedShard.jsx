import { useState } from "react";
import useNewsfeed from "./useNewsfeed";
import NewsStoryCard from "./NewsStoryCard";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"

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
        <Card>
            {data && data.map((story) => (
                <NewsStoryCard key={story.uuid} story={story}/>
            ))}
        </Card>
    );
}
