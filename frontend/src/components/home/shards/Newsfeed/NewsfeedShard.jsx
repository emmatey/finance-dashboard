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
import {
    Pagination,
    PaginationContent,
    PaginationEllipsis,
    PaginationItem,
    PaginationLink,
    PaginationNext,
    PaginationPrevious,
} from "@/components/ui/pagination"

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
    const [currentPage, setCurrentPage] = useState(0);
    if (loading) return <div>Loading...</div>;
    if (error) return <p>{`${error} ${responseCode}`}</p>;

    function calculatePageMemberIndices(data, pageSize, pageNumber) {
        const pageQty = Math.ceil(data.length / pageSize) - 1;

        if (pageNumber < 0 || pageNumber > pageQty || data.length === 0) {
            return [0, 0];
        }

        const lowBound = pageNumber * pageSize;
        const highBound = Math.min(lowBound + pageSize, data.length);

        return [lowBound, highBound];
    }

    
    return (
        <Card>
            <CardHeader>
                Newsfeed
            </CardHeader>
            {data && data.map((story) => (
                <NewsStoryCard key={story.uuid} story={story} />
            ))}
            <CardFooter>
                <Pagination>
                    <PaginationItem>
                        <PaginationPrevious
                            onClick={(event) => {
                                setCurrentPage((prevPage) => prevPage + -1)
                            }}
                            disabled={currentPage === 0 ? true : false}
                        />
                    </PaginationItem>

                    {

                    }

                    <PaginationItem>
                        <PaginationNext
                            onClick={(event) => {
                                setCurrentPage((prevPage) => prevPage + 1)
                            }}
                            disabled={currentPage === pageNumber ? true : false}
                        />
                    </PaginationItem>
                </Pagination>
            </CardFooter>
        </Card>
    );
}
