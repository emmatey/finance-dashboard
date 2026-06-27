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

function calculatePageMemberIndices(data, pageSize, pageNumber) {
    if (!data) return;
    const pageQty = Math.ceil(data.length / pageSize) - 1;

    if (pageNumber < 0 || pageNumber > pageQty || data.length === 0) {
        return [0, 0, 0];
    }

    const lowBound = pageNumber * pageSize;
    const highBound = Math.min(lowBound + pageSize, data.length);

    return [lowBound, highBound, pageQty];
}

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
    const [currentPage, setCurrentPage] = useState(0);
    const [resultsPerPage, setResultsPerPage] = useState(10);
    const { loading, data, error, responseCode } = useNewsfeed();
    if (loading) return <div>Loading...</div>;
    if (error) return <p>{`${error} ${responseCode}`}</p>;
    const [lowBound, highBound, pageQty] = data ? calculatePageMemberIndices(data, resultsPerPage, currentPage) : [0, 0, 0];
    let dataSubset = data ? data.slice(lowBound, highBound) : [];

    return (
        <Card>
            <CardHeader>
                Newsfeed
            </CardHeader>

            <CardContent>
                {dataSubset.map((data) => (<NewsStoryCard key={data.uuid} story={data} />))}
            </CardContent>

            <CardFooter className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-muted-foreground whitespace-nowrap">
                    <span>Per page:</span>
                    <select
                        value={resultsPerPage}
                        onChange={(e) => {
                            setResultsPerPage(Number(e.target.value));
                            setCurrentPage(0);
                        }}
                        className="h-8 w-16 rounded-md border border-input bg-background px-2 text-sm text-center outline-none cursor-pointer"
                    >
                        <option value={5}>5</option>
                        <option value={10}>10</option>
                        <option value={20}>20</option>
                        <option value={50}>50</option>
                    </select>
                </div>

                <Pagination className="w-auto mx-0">
                    <PaginationContent>
                        <PaginationItem>
                            <PaginationPrevious
                                onClick={(event) => {
                                    setCurrentPage((prevPage) => prevPage + -1)
                                }}
                                disabled={currentPage === 0 ? true : false}
                            />
                        </PaginationItem>

                        <PaginationItem>
                            {`${currentPage}/${pageQty}`}
                        </PaginationItem>

                        <PaginationItem>
                            <PaginationNext
                                onClick={(event) => {
                                    setCurrentPage((prevPage) => prevPage + 1)
                                }}
                                disabled={currentPage === pageQty ? true : false}
                            />
                        </PaginationItem>
                    </PaginationContent>
                </Pagination>
            </CardFooter>
        </Card>
    );
}
