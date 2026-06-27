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
/*
The loading initial-state flicker still stands. useNewsfeed still starts loading: false, so your first render (loading false, data null, error null) falls through both guards and paints an empty <Card> newsfeed for a frame before the effect flips loading to true. None of the context you pasted changes that — it's about the hook's initial state, not the pagination or the parser. Still think useState(true) is the truer starting point.
The "0/9" display still stands. {currentPage/{currentPage}/
currentPage/{pageQty}} is still showing zero-based indices to a human. pageQty is still really "last page index," not a count. Display-only +1 on both sides fixes the human-facing text without touching your slicing math.
<img> has no alt — that's over in NewsStoryCard, untouched here.
target="_blank" without rel — also in NewsStoryCard, untouched.
Unused imports in both NewsStoryCard and NewsfeedShard — untouched.
The cosmetic pair — disabled={currentPage === 0 ? true : false} (still a boolean asking to become a boolean) and prevPage + -1 (still the scenic route to - 1) — still there, still harmless, still made me smile. 😄
*/
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
/*

Your page-bound safety currently lives entirely in the view layer — it depends on PaginationLink's pointer-events-none doing its job, driven by your disabled={currentPage === 0} / disabled={currentPage === pageQty} props. Your handlers still don't clamp, and currentPage itself is never re-validated against pageQty. Today that's totally fine, because the only things that move currentPage are the two guarded buttons and the page-size <select> (which resets to 0). The invariant "currentPage is always within [0, pageQty]" holds.
The day it could break is the day data changes size after mount — a refresh/refetch that returns fewer stories, a filter, a search box, anything. If pageQty shrinks while you're sitting on a high page, nothing re-clamps currentPage, and since currentPage > pageQty makes neither === 0 nor === pageQty true, both buttons un-disable and you're stranded clicking around an empty feed. So the genuinely-robust move isn't "clamp the click handler" — it's a small useEffect that pulls currentPage back in range whenever pageQty changes, so the page index can never be left pointing past the end of the data. Park it for now; it's a "when this feed gets a refresh button" problem, not a today problem. But it's the real shape of what I was clumsily gesturing at the first time. 🧭
*/
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
