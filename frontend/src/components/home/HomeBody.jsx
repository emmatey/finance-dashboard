import { useState } from 'react'
import Header from '@/components/Header.jsx'
import { Card, CardContent } from '@/components/ui/card'
import ShardNav from './ShardNav'
import { SHARD_GROUPS } from './shardGroups'
import { ShardNavProvider } from '@/context/ShardNavContext.jsx'
import { ScreenersSelectionProvider } from '@/context/ScreenersSelectionContext.jsx'

export default function HomeBody() {
    const [activeGroupId, setActiveGroupId] = useState(SHARD_GROUPS[0].id);
    const activeGroup = SHARD_GROUPS.find((group) => group.id === activeGroupId);

    const [screenersSelected, setScreenersSelected] = useState([]);

    return (
        <ShardNavProvider value={{ activeGroupId, setActiveGroupId }}>
            <ScreenersSelectionProvider value={{ screenersSelected, setScreenersSelected }}>
                <div className="flex h-screen flex-col">
                    <Header />
                    <div className="flex flex-1 min-h-0 gap-4 p-4">
                        <ShardNav />

                        <main className="flex-1 min-h-0">
                            <Card className="h-full overflow-y-auto">
                                <CardContent className="flex flex-wrap items-start gap-4">
                                    {activeGroup.columns
                                        ? activeGroup.columns.map((shardIds, i) => (
                                            <div key={i} className="flex min-w-[320px] flex-1 flex-col gap-4">
                                                {shardIds.map((shardId) => {
                                                    const shard = activeGroup.shards.find((s) => s.id === shardId)
                                                    return <shard.component key={shardId} />
                                                })}
                                            </div>
                                        ))
                                        : activeGroup.shards.map((shard) => (
                                            <div key={shard.id} className="min-w-[320px] flex-1">
                                                <shard.component />
                                            </div>
                                        ))}
                                </CardContent>
                            </Card>
                        </main>
                    </div>
                </div>
            </ScreenersSelectionProvider>
        </ShardNavProvider>
    )
}
