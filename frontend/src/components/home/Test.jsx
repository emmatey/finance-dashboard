import ShardNav from "./ShardNav";
import ScreenersShard from "./shards/Screeners/ScreenersShard";
import { useShardNav } from "@/context/ShardNavContext";

export default function test() {
    console.log(useShardNav());
    return (
        <>
            <ShardNav />
        </>
    )
}