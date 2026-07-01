import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatCurrencyUSD } from '@/scripts/utils.js'
import useUserSummary from './useUserSummary'
import BalanceHistoryChart from "./BalanceHistory/BalanceHistoryChart";

export default function UserSummaryShard() {
    /* 
        cash_balance: 9650.181999999999
        grand_total: 9995.761999999999
        portfolio_value: 345.58
        rank: 1
        snap_datetime: "2026-06-30 22:04:23"
        user_id: 1
        username: "emma"
    */
    // TODO: Add 'today's gain/loss' feature here.

    const { loading, data, error, responseCode } = useUserSummary();

    if (loading) return <div>Loading...</div>;
    if (error) return <p className="text-sm text-destructive">{responseCode}{error}</p>;
    if (!data) return null;

    const lastUpdated = data.snap_datetime
        ? new Date(data.snap_datetime).toLocaleString()
        : null;

    return (
        <Card >
            <CardHeader>
                <CardTitle>
                    Account Value
                </CardTitle>
                <CardDescription>
                    Last updated on {lastUpdated}
                </CardDescription>
                <CardAction>
                    <Badge> Rank #{data["rank"]} </Badge>
                </CardAction>
            </CardHeader>
            <CardContent>
                <BalanceHistoryChart />
            </CardContent>
        </Card>
    );
}
