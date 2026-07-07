import { useState } from 'react'
import Header from '@/components/Header.jsx'
import { Card, CardContent } from '@/components/ui/card'
import ShardNav from './ShardNav'
import { SHARD_GROUPS } from './shardGroups'

export default function HomeBody() {
    const [activeGroupId, setActiveGroupId] = useState(SHARD_GROUPS[0].id)
    const activeGroup = SHARD_GROUPS.find((group) => group.id === activeGroupId)

    return (
        <div className="flex h-screen flex-col">
            <Header />
            <div className="flex flex-1 min-h-0 gap-4 p-4">
                <ShardNav activeGroupId={activeGroupId} onSelectGroup={setActiveGroupId} />

                <main className="flex-1 min-h-0">
                    <Card className="h-full overflow-y-auto">
                        <CardContent className="flex flex-wrap items-start gap-4">
                            {activeGroup.shards.map(({ id, component: ShardComponent }) => (
                                <div key={id} className="min-w-[320px] flex-1">
                                    <ShardComponent />
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </main>
            </div>
        </div>
    )
}
