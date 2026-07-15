import { useScreenersSelection } from "@/context/ScreenersSelectionContext";
import useScreenerData from "./useScreenerData";
import TableSkeleton from "@/components/TableSkeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function ScreenersShard() {
    const { screenersSelected, setScreenersSelected } = useScreenersSelection();
    const { dataLoading, errorMsg, screenerData } = useScreenerData();
    
    console.log(screenersSelected);
    let content = null;
    if (dataLoading) {
        content = <TableSkeleton />
    } else if (errorMsg) {
        content = <h1>{errorMsg}</h1>
    }

    return (
        <>
            {content && content}
            {!content && (
                <Tabs>
                    <TabsList>
                        {
                            screenersSelected.map((screener) => {
                                return (
                                    <TabsTrigger key={screener} value={screener}>{screener}</TabsTrigger>
                                )
                            })
                        }
                    </TabsList>
                </Tabs>
            )}
        </>
    )
}
