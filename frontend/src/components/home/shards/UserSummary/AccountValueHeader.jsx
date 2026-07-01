import {
    CardAction,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge";
import { formatCurrencyUSD, formatPercent } from '@/scripts/utils.js'
import { CHART_CONFIG } from './BalanceHistory/chartConfig'

function getTodayStartSeconds() {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime() / 1000;
}

// Always relative to the live current value, independent of what's being hovered on the chart -
// otherwise "today's change" would mean something different every time the mouse moves.
function getTodaysChange(history, activeLine, currentValue) {
    const todayStart = getTodayStartSeconds();
    const priorSnapshots = history.filter((snapshot) => snapshot.snap_datetime < todayStart);
    if (priorSnapshots.length === 0) return null;

    const baseline = priorSnapshots.reduce((latest, snapshot) => snapshot.snap_datetime > latest.snap_datetime ? snapshot : latest);
    const baselineValue = baseline[activeLine];
    const change = currentValue - baselineValue;
    const changePct = baselineValue !== 0 ? change / baselineValue : null;
    return { change, changePct };
}

export default function AccountValueHeader({ summary, history, hoveredPoint, activeLine }) {
    // Defaults to the live summary; swaps to the hovered chart point, snaps back on mouse-leave (hoveredPoint -> null)
    const displaySource = hoveredPoint ?? summary;
    const label = CHART_CONFIG[activeLine].label;
    // snap_datetime is epoch seconds (backend unixepoch()); Date expects ms, hence * 1000
    const lastUpdated = summary.snap_datetime
        ? new Date(summary.snap_datetime * 1000).toLocaleString()
        : null;

    const todaysChange = getTodaysChange(history, activeLine, summary[activeLine]);

    return (
        <CardHeader>
            <CardTitle>
                {formatCurrencyUSD(displaySource[activeLine])}
            </CardTitle>
            <CardDescription>
                {hoveredPoint ? label : `${label} · as of ${lastUpdated}`}
            </CardDescription>
            {todaysChange && (
                <p className={`text-sm ${todaysChange.change >= 0 ? "text-gain" : "text-destructive"}`}>
                    Today's Change {todaysChange.change >= 0 ? "+" : ""}{formatCurrencyUSD(todaysChange.change)}
                    {todaysChange.changePct != null && (
                        <> ({todaysChange.changePct >= 0 ? "+" : ""}{formatPercent(todaysChange.changePct)})</>
                    )}
                </p>
            )}
            <CardAction>
                <Badge> Rank #{summary.rank} </Badge>
            </CardAction>
        </CardHeader>
    );
}
