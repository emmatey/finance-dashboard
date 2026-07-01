import { Line, LineChart } from "recharts";
import { ChartContainer } from "@/components/ui/chart";
import { Button } from "@/components/ui/button";
import useBalanceHistory from "./useBalanceHistory"
import { Mobile } from "@hugeicons/core-free-icons";


export default function BalanceHistoryChart() {
    /*
        cash_balance: 10000
           grand_total: 10000
           portfolio_value: 0
           snap_datetime: "2026-06-08 05:08:50"
          username: "emma"
    */
    const { loading, data, error, responseCode } = useBalanceHistory();
    console.log(data);
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
            {
                loading ? (
                    <div>
                        <h2> Loading ... </h2>
                    </div>)
                    : (<>
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
                    </>)
            }
        </>
    )
}