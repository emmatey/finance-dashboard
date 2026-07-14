import ShardNav from "./ShardNav";
import ScreenersShard from "./shards/Screeners/ScreenersShard";
import { useShardNav } from "@/context/ShardNavContext";
import { useScreenersSelection } from "@/context/ScreenersSelectionContext";

export default function test() {
    console.log(useShardNav(), useScreenersSelection());
    return (
        <>
            <ShardNav />
        </>
    )
}