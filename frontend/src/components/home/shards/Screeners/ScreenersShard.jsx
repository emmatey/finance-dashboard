import { Button } from "@/components/ui/button";
import { useScreenersSelection } from "@/context/ScreenersSelectionContext"
import useScreenerData from "./useScreenerData";
import TableSkeleton from "@/components/TableSkeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import ScreenersTable from "./ScreenersTable";

export default function ScreenersShard() {
    const { screenersSelected, setScreenersSelected } = useScreenersSelection();
    const { dataLoading, errorMsg, screenerData } = useScreenerData(screenersSelected);

    let content = null;
    if (dataLoading) {
        content = <TableSkeleton />
    } else if (errorMsg) {
        content = <h1>{errorMsg}</h1>
    }
    return (
        <>
            {content && content}
            {!content && screenerData && (
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
                            const companiesList = screenerData[screener];
                            if (companiesList) {
                                return (
                                    <TabsContent key={screener} value={screener}>
                                        <ScreenersTable data={companiesList} />
                                    </TabsContent>
                                )
                            } else {
                                return (
                                    <TabsContent key={screener} value={screener}>
                                        <div className="flex">
                                            Oops {screener} is broken...
                                            <Button onClick={() => setScreenersSelected(screenersSelected.filter((i) => (i !== screener)))}>
                                                Remove from selected
                                            </Button>
                                        </div>
                                    </TabsContent>
                                )
                            }
                        })
                    }
                </Tabs>
            )}
        </>
    )
}
