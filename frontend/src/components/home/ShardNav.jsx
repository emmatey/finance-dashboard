import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { SHARD_GROUPS } from './shardGroups'
import { Card } from '@/components/ui/card'
import ScreenersLeftNav from './shards/Screeners/ScreenersLeftNav';
import { useShardNav } from '@/context/ShardNavContext';
import { cn } from '@/lib/utils'
import { ChevronLeftIcon, ChevronRightIcon } from 'lucide-react'

export default function ShardNav() {
    const { activeGroupId, setActiveGroupId } = useShardNav();
    const [collapsed, setCollapsed] = useState(false);

    return (
        <div
            className={cn(
                "relative h-full shrink-0 transition-all duration-200",
                collapsed ? "w-0" : activeGroupId === "screeners" ? "w-56" : "w-48"
            )}
        >
            <div className="h-full w-full overflow-hidden p-1">
                {activeGroupId === "screeners"
                    ?
                    <ScreenersLeftNav />
                    :
                    (
                        <Card className="flex h-full w-full flex-col gap-1 p-4">
                            {SHARD_GROUPS.map((group) => (
                                <Button
                                    key={group.id}
                                    variant={group.id === activeGroupId ? 'secondary' : 'ghost'}
                                    className="justify-start"
                                    onClick={() => setActiveGroupId(group.id)}
                                >
                                    {group.label}
                                </Button>
                            ))}
                        </Card>
                    )
                }
            </div>

            <Button
                variant="outline"
                size="icon-sm"
                aria-label={collapsed ? "Expand navigation" : "Collapse navigation"}
                onClick={() => setCollapsed((c) => !c)}
                className="absolute top-1/2 right-0 z-10 -translate-y-1/2 translate-x-1/2 rounded-full"
            >
                {collapsed ? <ChevronRightIcon className="size-4" /> : <ChevronLeftIcon className="size-4" />}
            </Button>
        </div>
    )
}
