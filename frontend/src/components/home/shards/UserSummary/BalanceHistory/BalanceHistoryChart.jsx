import { useState } from "react";
import { Line, LineChart } from "recharts";
import { ChartContainer } from "@/components/ui/chart";
import { Button } from "@/components/ui/button";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";


export default function BalanceHistoryChart({ data }) {
    const chartConfig = {
        cash_balance: {
            label: "Cash Balance",
            color: "var(--chart-1)"
        },
        portfolio_value: {
            label: "Holdings Value",
            color: "var(--chart-2)",
        },
        grand_total: {
            label: "Portfolio Value",
            color: "var(--chart-3)",
        }
    };

    const [activeLine, setActiveLine] = useState("grand_total");

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
                <LineChart data={data}>
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
            <div>
                <Button> 1m </Button>
                <Button> YTD </Button>
                <Button> 1yr </Button>
                <Button> All </Button>
            </div>
        </>
    )
}