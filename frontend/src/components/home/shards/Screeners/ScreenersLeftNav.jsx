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
    const {
        screenerCategoriesSelected,
        setScreenerCategoriesSelected,
        screenersSelected,
        setScreenersSelected
    } = useScreenersSelection();

    console.warn(screenersAvailable);
    const renderItem = (node) => {
        if (screenerCategoriesSelected.includes(node)) {
            return (
                <Collapsible key={node}>
                    <CollapsibleTrigger>
                        <div>
                            {node}
                        </div>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                        <div className="flex flex-col gap-1">
                            {screenersAvailable.node.map((child) => renderItem(child))}
                        </div>
                    </CollapsibleContent>
                </Collapsible>
            )
        }
        return (
            <CollapsibleTrigger>
                <ChevronRightIcon />
                {<Button> {node} </Button>}
            </CollapsibleTrigger>
        )
    }


    let content;
    if (availableLoading) {
        content = <Spinner />;
    } else if (errorMsg) {
        content = <p>{errorMsg}</p>;
    } else if (screenersAvailable) {
        content = (
            <>
                <CardContent>
                    <div className="flex flex-col gap-1">
                        {screenersAvailable.map((item) => renderItem(item))}
                    </div>
                </CardContent>
            </>
        );
    }

    return (
        <Card className="flex h-full w-48 shrink-0 flex-col gap-1 p-4">
            <CardHeader>
                <CardAction onClick={() => console.log("clicked")}>
                    <Badge />
                </CardAction>
            </CardHeader>
            <CardContent>
                {content}
            </CardContent>
        </Card>
    )
}