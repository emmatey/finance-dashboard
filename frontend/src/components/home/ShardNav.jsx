import { Button } from '@/components/ui/button'
import { SHARD_GROUPS } from './shardGroups'
import { Card } from '@/components/ui/card'
import { useShardNav } from '@/context/ShardNavContext'

export default function ShardNav({ activeGroupId, onSelectGroup }) {
    const activeShardGroup = useShardNav().activeGroupId;
    console.log(activeShardGroup);
    return (
        <>
            {activeShardGroup === "screeners"
                ?
                <Card className="flex h-full w-48 shrink-0 flex-col gap-1 p-4">
                    <span> 
                        Test
                    </span>
                </Card>
                :
                (
                    <Card className="flex h-full w-48 shrink-0 flex-col gap-1 p-4">
                        {SHARD_GROUPS.map((group) => (
                            <Button
                                key={group.id}
                                variant={group.id === activeGroupId ? 'secondary' : 'ghost'}
                                className="justify-start"
                                onClick={() => onSelectGroup(group.id)}
                            >
                                {group.label}
                            </Button>
                        ))}
                    </Card>
                )
            }
        </>
    )
}
