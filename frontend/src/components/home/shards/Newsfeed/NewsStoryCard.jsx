import { Button } from "@/components/ui/button"
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
import { formatUTCSeconds } from "@/scripts/utils"


export default function NewsStoryCard({ story }) {
    /*
        data: [{
            uuid: str,
            title: str,
            link: str,
            publisher: str,
            thumbnail: str,
            providerPublishTime: int
        }]
    */
    /*
        This card will be a horizontal rectangle that contains the thumbnail on the left
        a clickable title in the body
        the publisher below, and the date on the second line as well. 

        This card needs the state for one story. However the parent should control the visibility and
        the lifecycle.
    */
    function handleClick() {
        if (story?.link) {
            window.open(story.link, '_blank', 'noopener,noreferrer');
        }
    }

    return (
        <Card className='flex flex-row bg-secondary' onClick={handleClick}>
            <div className="flex-shrink-0 p-4">
                <img
                    src={story?.thumbnail}
                    className="w-16 h-16 object-cover rounded"
                    onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = '/images/searchBar/newsIcon.svg'
                    }}
                    alt="Article thumbnail."
                />
            </div>
            <CardContent>
                <span>
                    {story?.title ?? "title not found..."}
                </span>
                <CardDescription>
                    {story?.publisher ?? "publisher not found"}
                </CardDescription>
                <CardDescription>
                    {story?.providerPublishTime ? formatUTCSeconds(story.providerPublishTime) : "publish time not found."}
                </CardDescription>
            </CardContent>
        </Card>
    )
}