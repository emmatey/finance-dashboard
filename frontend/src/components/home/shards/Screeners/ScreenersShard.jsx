import { Button } from "@/components/ui/button";
import { useScreenersSelection } from "@/context/ScreenersSelectionContext"
import useScreenerData from "./useScreenerData";
import useAvailableScreeners from "./useAvailableScreeners";
import TableSkeleton from "@/components/TableSkeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import ScreenersTable from "./ScreenersTable";
import { useState, useEffect } from "react";
import { RotateCwIcon, XIcon } from "lucide-react";
import { parseResponse } from "@/scripts/utils";
import { cn } from "@/lib/utils";

export default function ScreenersShard() {
    const { screenersSelected, setScreenersSelected } = useScreenersSelection();
    const [screenerCache, setScreenerCache] = useState({});
    const [refreshing, setRefreshing] = useState(false);
    const { screenersAvailable } = useAvailableScreeners();
    let toSearch = screenersSelected.filter((screener) => (!Object.keys(screenerCache).includes(screener)));
    const { dataLoading, errorMsg, screenerData } = useScreenerData(toSearch);

    useEffect(() => {
        let cache = {...screenerCache};
        for (const [screener, data] of Object.entries(screenerData)) {
            cache[screener] = data;
        };
        setScreenerCache(cache);
    }, [screenerData]);

    async function refreshScreeners() {
        const customScreenerNames = screenersAvailable?.custom ?? [];
        const hasCustomSelected = screenersSelected.some((s) => customScreenerNames.includes(s));

        if (!hasCustomSelected) {
            setScreenerCache({});
            return;
        }

        setRefreshing(true);
        try {
            const res = await fetch('/api/screeners/refresh_custom', { method: 'POST' });
            await parseResponse(res);
        } catch (error) {
            console.error(error);
        } finally {
            setRefreshing(false);
            setScreenerCache({});
        }
    }

    function unSelectAllScreeners() {
        setScreenersSelected([]);
    }

    function removeScreener(screener) {
        setScreenersSelected(screenersSelected.filter((i) => i !== screener));
    }

    return (
        <>
            <div className="mb-3 flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={refreshScreeners} disabled={refreshing}>
                    <RotateCwIcon className={cn("size-3.5", refreshing && "animate-spin")} />
                    Refresh
                </Button>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={unSelectAllScreeners}
                    disabled={screenersSelected.length === 0}
                >
                    <XIcon className="size-3.5" />
                    Clear All
                </Button>
            </div>
            {screenersSelected.length > 0 ? (
                <Tabs defaultValue={screenersSelected[0]}>
                    <TabsList>
                        {
                            screenersSelected.map((screener) => {
                                return (
                                    <div key={screener} className="relative">
                                        <TabsTrigger value={screener} className="pr-6">
                                            {screener}
                                        </TabsTrigger>
                                        <span
                                            role="button"
                                            tabIndex={0}
                                            aria-label={`Remove ${screener}`}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                removeScreener(screener);
                                            }}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter' || e.key === ' ') {
                                                    e.preventDefault();
                                                    e.stopPropagation();
                                                    removeScreener(screener);
                                                }
                                            }}
                                            className="absolute top-1/2 right-1 -translate-y-1/2 rounded-full p-0.5 text-foreground/50 hover:bg-background hover:text-foreground"
                                        >
                                            <XIcon className="size-3" />
                                        </span>
                                    </div>
                                )
                            })
                        }
                    </TabsList>
                    {
                        screenersSelected.map((screener) => {
                            const companiesObjectList = screenerCache[screener];
                            return (
                                <TabsContent key={screener} value={screener}>
                                    {companiesObjectList ? (
                                        <ScreenersTable data={companiesObjectList} />
                                    ) : dataLoading ? (
                                        <TableSkeleton />
                                    ) : (
                                        <div className="flex items-center gap-2">
                                            <span>Oops {screener} is broken...</span>
                                            <Button variant="outline" size="sm" onClick={() => removeScreener(screener)}>
                                                Remove from selected
                                            </Button>
                                        </div>
                                    )}
                                </TabsContent>
                            )
                        })
                    }
                </Tabs>
            ) :
            <p className="text-sm text-muted-foreground"> Select screeners to begin. </p>}
        </>
    )
}
