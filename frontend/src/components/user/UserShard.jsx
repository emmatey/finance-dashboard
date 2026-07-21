import { Card, CardHeader, CardTitle, CardDescription, CardAction, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatCurrencyUSD } from "@/scripts/utils"
import useUserSummary from "@/components/home/shards/UserSummary/useUserSummary"
import Holdings from "@/components/home/shards/Portfolio/Holdings/Holdings"

export default function UserShard({ username }) {
    const { loading, data: summary, error } = useUserSummary(username);

    return (
        <>
            <Card>
                {loading && <CardHeader><p>Loading...</p></CardHeader>}
                {error && <CardHeader><p className="text-sm text-destructive">{error}</p></CardHeader>}
                {!loading && !error && summary && (
                    <CardHeader>
                        <CardTitle>{summary.username}</CardTitle>
                        <CardDescription>
                            Balance {formatCurrencyUSD(summary.cash_balance)} · Account Value {formatCurrencyUSD(summary.grand_total)}
                        </CardDescription>
                        <CardAction>
                            <Badge>Rank #{summary.rank}</Badge>
                        </CardAction>
                    </CardHeader>
                )}
            </Card>
            <Card>
                <CardHeader>
                    <CardTitle>Holdings</CardTitle>
                </CardHeader>
                <CardContent>
                    <Holdings username={username} />
                </CardContent>
            </Card>
        </>
    )
}
