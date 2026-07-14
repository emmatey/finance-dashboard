import { Card, CardAction, CardContent, CardHeader } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { useShardNav } from '@/context/ShardNavContext'
import useAvailableScreeners from "./useAvailableScreeners";
import { Badge } from "@/components/ui/badge";


export default function ScreenersLeftNav() {
    const { setActiveGroupId } = useShardNav();
    const { availableLoading, errorMsg, screenersAvailable } = useAvailableScreeners();

    let content;
    if (availableLoading) {
        content = <Spinner />;
    } else if (errorMsg) {
        content = <p>{errorMsg}</p>;
    } else if (screenersAvailable) {
        content = (
            <>
                <button onClick={() => setActiveGroupId("home")}> Go Back </button>
                {screenersAvailable.map((category, i) => (
                    <Collapsible key={i}>
                        <CollapsibleTrigger> {">"} </CollapsibleTrigger>
                        {category.map((company, j) => (
                            <CollapsibleContent key={j}>
                                <span> {company} </span>
                            </CollapsibleContent>
                        ))}
                    </Collapsible>
                ))}
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