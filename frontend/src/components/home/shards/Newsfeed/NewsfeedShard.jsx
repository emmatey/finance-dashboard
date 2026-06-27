import { useEffect, useState } from "react";
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
    const lastPage = Math.ceil(data.length / pageSize) - 1;

    if (pageNumber < 0 || pageNumber > lastPage || data.length === 0) {
        return [0, 0, 0];
    }

    const lowBound = pageNumber * pageSize;
    const highBound = Math.min(lowBound + pageSize, data.length);

    return [lowBound, highBound, lastPage];
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
    useEffect(() => {
        setCurrentPage(0);
        }, [data]);

    if (loading) return <div>Loading...</div>;
    if (error) return <p>{`${error} ${responseCode}`}</p>;
    const [lowBound, highBound, lastPage] = data ? calculatePageMemberIndices(data, resultsPerPage, currentPage) : [0, 0, 0];
    let dataSubset = data ? data.slice(lowBound, highBound) : [];

    return (
        <Card className={'bg-accent'}>
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
                                onClick={() => {
                                    setCurrentPage((prevPage) => prevPage - 1)
                                }}
                                disabled={currentPage === 0}
                            />
                        </PaginationItem>

                        <PaginationItem>
                            {`${currentPage + 1}/${lastPage + 1}`}
                        </PaginationItem>

                        <PaginationItem>
                            <PaginationNext
                                onClick={() => {
                                    setCurrentPage((prevPage) => prevPage + 1)
                                }}
                                disabled={currentPage === lastPage ? true : false}
                            />
                        </PaginationItem>
                    </PaginationContent>
                </Pagination>
            </CardFooter>
        </Card>
    );
}
