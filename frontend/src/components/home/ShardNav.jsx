import { Button } from '@/components/ui/button'
import { SHARD_GROUPS } from './shardGroups'
import { Card } from '../ui/card'

export default function ShardNav({ activeGroupId, onSelectGroup }) {
    return (
        <Card className="flex w-48 shrink-0 flex-col gap-1 p-4">
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
