import { useState } from "react";
import { Line, LineChart, XAxis, YAxis } from "recharts";
import { ChartContainer } from "@/components/ui/chart";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { CHART_CONFIG } from "./chartConfig";
import { formatUTCSeconds, formatCurrencyUSD } from "@/scripts/utils.js";

const DAY_IN_SECONDS = 24 * 60 * 60;

const RANGE_OPTIONS = ["1m", "YTD", "1yr", "All"];

// snap_datetime from the backend (unixepoch()) is epoch seconds; Date/getTime() are ms, hence the / 1000 below
function getRangeCutoffSeconds(range) {
    const nowSeconds = Date.now() / 1000;
    const currentYear = new Date().getFullYear();
    switch (range) {
        case "1m":
            return nowSeconds - 30 * DAY_IN_SECONDS;
        case "YTD": {
            return new Date(currentYear, 0, 1).getTime() / 1000;
        }
        case "1yr":
            return nowSeconds - 365 * DAY_IN_SECONDS;
        case "All":
        default:
            return null;
    }
}

export default function BalanceHistoryChart({ data, activeLine, onActiveLineChange, onHoverChange }) {
    const [activeRange, setActiveRange] = useState("1yr");

    const rangeCutoff = getRangeCutoffSeconds(activeRange);
    const rangedData = rangeCutoff ? data.filter((d) => d.snap_datetime >= rangeCutoff) : data;

    function handleMouseMove(nextState) {
        // activeTooltipIndex comes back as a string (e.g. "2"), not a number - Number() it before indexing
        if (nextState.isTooltipActive && nextState.activeTooltipIndex != null) {
            onHoverChange(rangedData[Number(nextState.activeTooltipIndex)] ?? null);
        } else {
            onHoverChange(null);
        }
    }

    return (
        <>
            <ToggleGroup
                type="single"
                variant="outline"
                value={activeLine}
                onValueChange={(value) => value && onActiveLineChange(value)}
            >
                {Object.entries(CHART_CONFIG).map(([dataKey, { label, color }]) => (
                    <ToggleGroupItem key={dataKey} value={dataKey} aria-label={`Show ${label}`}>
                        <span className="size-2 rounded-full" style={{ backgroundColor: color }} />
                        {label}
                    </ToggleGroupItem>
                ))}
            </ToggleGroup>
            <ChartContainer config={CHART_CONFIG} className="h-56 w-full pt-4">
                <LineChart data={rangedData} onMouseMove={handleMouseMove} onMouseLeave={() => onHoverChange(null)}>
                    <XAxis dataKey="snap_datetime" tickFormatter={formatUTCSeconds} />
                    <YAxis tickFormatter={formatCurrencyUSD} width={80} />
                    {Object.keys(CHART_CONFIG).map((dataKey) => (
                        <Line
                            key={dataKey}
                            dataKey={dataKey}
                            stroke={`var(--color-${dataKey})`}
                            hide={dataKey !== activeLine}
                        />
                    ))}
                </LineChart>
            </ChartContainer>
            <ToggleGroup
                type="single"
                variant="outline"
                className="mx-auto"
                value={activeRange}
                onValueChange={(value) => value && setActiveRange(value)}
            >
                {RANGE_OPTIONS.map((range) => (
                    <ToggleGroupItem key={range} value={range} aria-label={`Show ${range} range`}>
                        {range}
                    </ToggleGroupItem>
                ))}
            </ToggleGroup>
        </>
    )
}