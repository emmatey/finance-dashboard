import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge";
import useUserSummary from './useUserSummary'
import useBalanceHistory from './BalanceHistory/useBalanceHistory'
import BalanceHistoryChart from "./BalanceHistory/BalanceHistoryChart";

export default function UserSummaryShard() {
    // TODO: Add 'today's gain/loss' feature here.

    const { loading: summaryLoading, data: summary, error: summaryError, responseCode: summaryResponseCode } = useUserSummary();
    const { loading: historyLoading, data: history, error: historyError, responseCode: historyResponseCode } = useBalanceHistory();

    const loading = summaryLoading || historyLoading;
    const error = summaryError || historyError;
    const responseCode = error ? (summaryError ? summaryResponseCode : historyResponseCode) : null;

    if (loading) return <div>Loading...</div>;
    if (error) return <p className="text-sm text-destructive">{responseCode}{error}</p>;
    if (!summary) return null;

    const lastUpdated = summary.snap_datetime
        ? new Date(summary.snap_datetime * 1000).toLocaleString()
        : null;

    return (
        <Card>
            <CardHeader>
                <CardTitle>
                    Account Value
                </CardTitle>
                <CardDescription>
                    Last updated on {lastUpdated}
                </CardDescription>
                <CardAction>
                    <Badge> Rank #{summary.rank} </Badge>
                </CardAction>
            </CardHeader>
            <CardContent>
                <BalanceHistoryChart data={history} />
            </CardContent>
        </Card>
    );
}
