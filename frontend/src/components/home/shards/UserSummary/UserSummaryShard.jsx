import { Card, CardContent } from '@/components/ui/card.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { formatCurrencyUSD } from '@/scripts/utils.js'
import useUserSummary from './useUserSummary'

export default function UserSummaryShard() {
    const { loading, data, error, responseCode } = useUserSummary();

    if (loading) return <div>Loading...</div>;
    if (error) return <p className="text-sm text-destructive">{error}</p>;
    if (!data) return null;

    const lastUpdated = data.snap_datetime
        ? new Date(data.snap_datetime).toLocaleString()
        : null;

    return (
        <Card className="w-full">
            <CardContent className="p-6">

                {/* Header: username + rank */}
                <div className="flex items-start justify-between mb-1">
                    <p className="text-muted-foreground text-sm">Welcome back,</p>
                    <span className="text-xs font-medium text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
                        Rank #{data.rank ?? '—'}
                    </span>
                </div>
                <p className="text-2xl font-semibold mb-4">{data.username}</p>

                <Separator className="mb-4" />

                {/* Total account value */}
                <p className="text-sm text-muted-foreground mb-1">Total Account Value</p>
                <p className="text-4xl font-bold tracking-tight mb-6">
                    {formatCurrencyUSD(data.grand_total)}
                </p>

                {/* Portfolio vs Cash breakdown */}
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <p className="text-xs text-muted-foreground mb-0.5">Invested</p>
                        <p className="text-xl font-semibold">{formatCurrencyUSD(data.portfolio_value)}</p>
                    </div>
                    <div>
                        <p className="text-xs text-muted-foreground mb-0.5">Cash</p>
                        <p className="text-xl font-semibold">{formatCurrencyUSD(data.cash_balance)}</p>
                    </div>
                </div>

                {/* Last updated */}
                {lastUpdated && (
                    <p className="text-xs text-muted-foreground mt-4">
                        Updated {lastUpdated}
                    </p>
                )}

            </CardContent>
        </Card>
    );
}
