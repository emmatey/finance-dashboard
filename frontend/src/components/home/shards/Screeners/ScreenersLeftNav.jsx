import { Card, CardAction, CardContent, CardHeader } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { useShardNav } from '@/context/ShardNavContext'
import useAvailableScreeners from "./useAvailableScreeners";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import { ChevronDownIcon } from "@hugeicons/core-free-icons";
import { cn } from "@/lib/utils";


export default function ScreenersLeftNav() {
    const { setActiveGroupId, screenersSelected, setScreenersSelected } = useShardNav();
    const { availableLoading, errorMsg, screenersAvailable } = useAvailableScreeners();
    const [categoriesOpen, setCategoriesOpen] = useState([]);

    const handleCategoryClick = (categoryName) => {
        setCategoriesOpen((latestCategoriesOpen) => {
            if (latestCategoriesOpen.includes(categoryName)) {
                return latestCategoriesOpen.filter((screener) => (screener !== categoryName));
            } else {
                return [...latestCategoriesOpen, categoryName]
            };
        })
    }

    const handleScreenerClick = (screenerName) => {
    };

    let content;
    if (availableLoading) {
        content = <Spinner />;
    } else if (errorMsg) {
        content = <p>{errorMsg}</p>;
    } else if (screenersAvailable) {
        content = (
            <>
                <button onClick={() => setActiveGroupId("home")}> Go Back </button>
                {Object.entries(screenersAvailable).map(([categoryName, screenerNames]) => (
                    <Collapsible key={categoryName}>
                        <CollapsibleTrigger onClick={handleCategoryClick} className="flex w-full items-center justify-between">
                            {categoryName}
                            <HugeiconsIcon
                                icon={ChevronDownIcon}
                                className={cn(
                                    "size-4 text-muted-foreground transition-transform duration-200",
                                    !categoriesOpen.includes(categoryName) ? "-rotate-90" : "rotate-0"
                                )}
                            />
                        </CollapsibleTrigger>
                        {screenerNames.map((screenerName) => (
                            <CollapsibleContent key={screenerName}>
                                <div key={screenerName} onClick={handleScreenerClick} className={cn(
                                    {}
                                )}>

                                </div>
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