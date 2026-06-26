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


export default function NewsStoryCard({story}) {
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
    return (
        <Card>
            <CardHeader>
                <img 
                    src={story?.thumbnail}
                    onError={(e) => {
                        e.target.onError = null;
                        e.target.src = 'images/searchBar/newsIcon.svg'
                    }}
                />
                <CardAction>
                
                </CardAction>
            </CardHeader>
            <CardContent>

            </CardContent>
            <CardDescription>

            </CardDescription>
        </Card>
        
    )
}