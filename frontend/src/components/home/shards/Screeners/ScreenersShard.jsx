import { Button } from "@/components/ui/button";
import { useScreenersSelection } from "@/context/ScreenersSelectionContext"
import useScreenerData from "./useScreenerData";
import TableSkeleton from "@/components/TableSkeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import ScreenersTable from "./ScreenersTable";
import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";

export default function ScreenersShard() {
    const { screenersSelected, setScreenersSelected } = useScreenersSelection();
    const [screenerCache, setScreenerCache] = useState({});
    let toSearch = screenersSelected.filter((screener) => (!Object.keys(screenerCache).includes(screener)));
    const { dataLoading, errorMsg, screenerData } = useScreenerData(toSearch);

    useEffect(() => {
        let cache = {...screenerCache};
        for (const [screener, data] of Object.entries(screenerData)) {
            cache[screener] = data;
        };
        setScreenerCache(cache);
    }, [screenerData]);

    function refreshScreeners() {
        setScreenerCache({});
    }

    function unSelectAllScreeners() {
        setScreenersSelected([]);
    }

    return (
        <>
            <div>
                <Badge onClick={refreshScreeners}>Refresh</Badge>
                <Badge onClick={unSelectAllScreeners}>Clear-All</Badge>
            </div>
            {screenersSelected.length > 0 ? (
                <Tabs>
                    <TabsList>
                        {
                            screenersSelected.map((screener) => {
                                return <TabsTrigger key={screener} value={screener}>{screener}</TabsTrigger>
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
                                        <div className="flex">
                                            Oops {screener} is broken...
                                            <Button onClick={() => setScreenersSelected(screenersSelected.filter((i) => (i !== screener)))}>
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
            <p> Select screeners to begin. </p>}
        </>
    )
}
