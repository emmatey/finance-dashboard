import { useState } from "react";
import { Line, LineChart } from "recharts";
import { ChartContainer } from "@/components/ui/chart";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

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

export default function BalanceHistoryChart({ data }) {
    const chartConfig = {
        grand_total: {
            label: "Portfolio Value",
            color: "var(--chart-3)",
        },
        cash_balance: {
            label: "Cash Balance",
            color: "var(--chart-1)"
        },
        portfolio_value: {
            label: "Holdings Value",
            color: "var(--chart-2)",
        }
    };

    const [activeLine, setActiveLine] = useState("grand_total");
    const [activeRange, setActiveRange] = useState("1yr");

    const rangeCutoff = getRangeCutoffSeconds(activeRange);
    const rangedData = rangeCutoff ? data.filter((d) => d.snap_datetime >= rangeCutoff) : data;

    return (
        <>
            <ToggleGroup
                type="single"
                variant="outline"
                value={activeLine}
                onValueChange={(value) => value && setActiveLine(value)}
            >
                {Object.entries(chartConfig).map(([dataKey, { label, color }]) => (
                    <ToggleGroupItem key={dataKey} value={dataKey} aria-label={`Show ${label}`}>
                        <span className="size-2 rounded-full" style={{ backgroundColor: color }} />
                        {label}
                    </ToggleGroupItem>
                ))}
            </ToggleGroup>
            <ChartContainer config={chartConfig}>
                <LineChart data={rangedData}>
                    {Object.keys(chartConfig).map((dataKey) => (
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