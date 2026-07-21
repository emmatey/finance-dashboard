import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Spinner } from "@/components/ui/spinner";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { useShardNav } from '@/context/ShardNavContext'
import { useScreenersSelection } from '@/context/ScreenersSelectionContext'
import useAvailableScreeners from "./useAvailableScreeners";
import { cn } from "@/lib/utils";
import { ChevronRightIcon, FileIcon, FolderIcon, XIcon } from "lucide-react"


export default function ScreenersLeftNav() {
    const { setActiveGroupId } = useShardNav();
    const { availableLoading, errorMsg, screenersAvailable } = useAvailableScreeners();
    const { screenersSelected, setScreenersSelected } = useScreenersSelection();

    function toggleSelect(item) {
        if (screenersSelected.includes(item)) {
            setScreenersSelected(prev => prev.filter((i) => i !== item));
        } else {
            setScreenersSelected(prev => [...prev, item]);
        };
    }

    let content;
    if (availableLoading) {
        content = (
            <div className="flex items-center justify-center py-4">
                <Spinner className="size-5" />
            </div>
        );
    } else if (errorMsg) {
        content = <p className="text-sm text-destructive">{errorMsg}</p>;
    } else if (screenersAvailable) {
        content = (
            <div className="flex flex-col gap-1">
                {
                    Object.entries(screenersAvailable).map(([key, value]) => {
                        return (
                            <Collapsible key={key}>
                                <CollapsibleTrigger className="group flex w-full items-center gap-1.5 rounded-lg px-2 py-1.5 text-sm font-medium text-foreground hover:bg-muted">
                                    <ChevronRightIcon className="size-3.5 shrink-0 text-muted-foreground transition-transform group-data-[state=open]:rotate-90" />
                                    <FolderIcon className="size-3.5 shrink-0 text-muted-foreground" />
                                    <span className="truncate">{key}</span>
                                </CollapsibleTrigger>
                                <CollapsibleContent className="ml-2.5 flex flex-col gap-0.5 border-l border-border py-0.5 pl-2.5">
                                    {value.map((screener) => (
                                        <button
                                            key={screener}
                                            type="button"
                                            onClick={() => toggleSelect(screener)}
                                            className={cn(
                                                "flex items-center gap-1.5 rounded-lg px-2 py-1 text-left text-sm transition-colors hover:bg-muted",
                                                screenersSelected.includes(screener)
                                                    ? "bg-muted font-medium text-primary"
                                                    : "text-muted-foreground hover:text-foreground"
                                            )}
                                        >
                                            <FileIcon className="size-3.5 shrink-0" />
                                            <span className="truncate">{screener}</span>
                                        </button>
                                    ))}
                                </CollapsibleContent>
                            </Collapsible>
                        )
                    })
                }
            </div>
        );
    }

    return (
        <Card className="h-full w-56 shrink-0 gap-0 py-3">
            <CardContent className="flex items-center justify-between px-3">
                <span className="text-sm font-semibold">Screeners</span>
                <Button
                    variant="ghost"
                    size="icon-sm"
                    aria-label="Close screeners"
                    onClick={() => setActiveGroupId("home")}
                >
                    <XIcon className="size-4" />
                </Button>
            </CardContent>
            <Separator className="my-2" />
            <CardContent className="min-h-0 flex-1 overflow-y-auto px-3">
                {content}
            </CardContent>
        </Card>
    )
}
