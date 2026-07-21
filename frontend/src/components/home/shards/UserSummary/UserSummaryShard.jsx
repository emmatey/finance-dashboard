import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"
import useUserSummary from './useUserSummary'
import useBalanceHistory from './BalanceHistory/useBalanceHistory'
import AccountValueHeader from './AccountValueHeader'
import BalanceHistoryChart from "./BalanceHistory/BalanceHistoryChart";

export default function UserSummaryShard() {
    const { loading: summaryLoading, data: summary, error: summaryError, responseCode: summaryResponseCode } = useUserSummary();
    const { loading: historyLoading, data: history, error: historyError, responseCode: historyResponseCode } = useBalanceHistory();

    const [activeLine, setActiveLine] = useState("grand_total");
    const [hoveredPoint, setHoveredPoint] = useState(null);

    const loading = summaryLoading || historyLoading;
    const error = summaryError || historyError;
    const responseCode = error ? (summaryError ? summaryResponseCode : historyResponseCode) : null;

    if (loading) {
        return (
            <Card>
                <CardContent className="flex items-center justify-center py-8">
                    <Spinner className="size-6" />
                </CardContent>
            </Card>
        );
    }
    if (error) return <p className="text-sm text-destructive">{responseCode}{error}</p>;
    if (!summary) return null;

    return (
        <Card>
            <AccountValueHeader summary={summary} history={history} hoveredPoint={hoveredPoint} activeLine={activeLine} />
            <CardContent>
                <BalanceHistoryChart
                    data={history}
                    activeLine={activeLine}
                    onActiveLineChange={setActiveLine}
                    onHoverChange={setHoveredPoint}
                />
            </CardContent>
        </Card>
    );
}
