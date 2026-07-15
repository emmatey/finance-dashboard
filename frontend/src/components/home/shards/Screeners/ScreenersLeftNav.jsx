import { Card, CardAction, CardContent, CardHeader } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { useShardNav } from '@/context/ShardNavContext'
import { useScreenersSelection } from '@/context/ScreenersSelectionContext'
import useAvailableScreeners from "./useAvailableScreeners";
import { Badge } from "@/components/ui/badge";
import { ChevronRightIcon, ChevronDownIcon, FileIcon, FolderIcon } from "lucide-react"


export default function ScreenersLeftNav() {
    const { setActiveGroupId } = useShardNav();
    const { availableLoading, errorMsg, screenersAvailable } = useAvailableScreeners();
    const { screenersSelected, setScreenersSelected } = useScreenersSelection();

    function toggleSelect(e) {
        const item = e.target.firstChild.data;
        if (screenersSelected.includes(item)) {
            setScreenersSelected(prev => prev.filter((i) => i !== item));
        } else {
            setScreenersSelected(prev => [...prev, item]);
        };
    }

    let content;
    if (availableLoading) {
        content = <Spinner />;
    } else if (errorMsg) {
        content = <p>{errorMsg}</p>;
    } else if (screenersAvailable) {
        content = (
            <>
                {
                    Object.entries(screenersAvailable).map(([key, value]) => {
                        return (
                            <Collapsible key={key}>
                                <CollapsibleTrigger>
                                    <Badge>{key}</Badge>
                                </CollapsibleTrigger>
                                {
                                    value.map((screener) => {
                                        return (
                                            <CollapsibleContent key={screener}>
                                                {<div className={
                                                    screenersSelected.includes(screener)
                                                        ?
                                                        "text-primary font-medium"
                                                        :
                                                        "text-muted-foreground hover:text-foreground"
                                                }
                                                    onClick={toggleSelect}>
                                                    {screener}
                                                </div>}
                                            </CollapsibleContent>
                                        )
                                    })
                                }
                            </Collapsible>
                        )
                    })
                }
            </>
        );
    }

    return (
        <Card className="flex h-full w-48 shrink-0 flex-col gap-1 p-4">
            <CardHeader>
                <CardAction onClick={() => setActiveGroupId("home")}>
                    <Badge />
                </CardAction>
            </CardHeader>
            <CardContent>
                {content}
            </CardContent>
        </Card>
    )
}