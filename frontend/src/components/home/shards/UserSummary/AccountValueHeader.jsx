import {
    CardAction,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge";
import { formatCurrencyUSD } from '@/scripts/utils.js'
import { CHART_CONFIG } from './BalanceHistory/chartConfig'

export default function AccountValueHeader({ summary, hoveredPoint, activeLine }) {
    // Defaults to the live summary; swaps to the hovered chart point, snaps back on mouse-leave (hoveredPoint -> null)
    const displaySource = hoveredPoint ?? summary;
    const label = CHART_CONFIG[activeLine].label;
    // snap_datetime is epoch seconds (backend unixepoch()); Date expects ms, hence * 1000
    const lastUpdated = summary.snap_datetime
        ? new Date(summary.snap_datetime * 1000).toLocaleString()
        : null;

    return (
        <CardHeader>
            <CardTitle>
                {formatCurrencyUSD(displaySource[activeLine])}
            </CardTitle>
            <CardDescription>
                {hoveredPoint ? label : `${label} · as of ${lastUpdated}`}
            </CardDescription>
            <CardAction>
                <Badge> Rank #{summary.rank} </Badge>
            </CardAction>
        </CardHeader>
    );
}
