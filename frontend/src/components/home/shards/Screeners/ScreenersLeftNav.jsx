import { Card } from "@/components/ui/card"
import { useShardNav } from '@/context/ShardNavContext'


export default function ScreenersLeftNav() {
    const { activeGroupId, setActiveGroupId } = useShardNav();

    return (
        <Card className="flex h-full w-48 shrink-0 flex-col gap-1 p-4">
            <span>
                Under Construction!
            </span>
            <button onClick={() => setActiveGroupId("home")}> Go Back </button>
        </Card>
    )
}