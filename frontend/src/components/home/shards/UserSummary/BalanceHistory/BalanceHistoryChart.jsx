import { Line, LineChart } from "recharts";
import { ChartContainer } from "@/components/ui/chart";
import { Button } from "@/components/ui/button";


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

    return (
        <>
            <ChartContainer config={chartConfig}>
                <LineChart data={data}>
                    <Line dataKey="cash_balance" />
                    <Line dataKey="portfolio_value" />
                    <Line dataKey="grand_total" />
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