import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Spinner } from '@/components/ui/spinner'
import { formatCurrencyUSD, getMarketStateBadge } from '@/scripts/utils.js'
import useHoldings from '@/components/home/shards/Portfolio/Holdings/useHoldings'

export default function HoldingsCard({ ticker }) {
    const { loading, data, error } = useHoldings();
    const holding = data?.find((row) => row.symbol === ticker);
    const marketStateBadge = holding ? getMarketStateBadge(holding.market_state) : null;

    return (
        <Card className="flex h-full flex-col">
            <CardHeader>
                <CardTitle>Your Holdings</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-1 flex-col">
                {loading ? (
                    <div className="flex flex-1 items-center justify-center">
                        <Spinner className="size-5" />
                    </div>
                ) : error ? (
                    <p className="flex-1 text-sm text-muted-foreground">{error}</p>
                ) : holding ? (
                    <div className="flex-1 space-y-1.5 text-sm">
                        <div className="mb-2 flex items-center justify-between">
                            <span className="text-2xl font-bold">{formatCurrencyUSD(holding.current_value)}</span>
                            {marketStateBadge && (
                                <Badge variant={marketStateBadge.variant}>{marketStateBadge.label}</Badge>
                            )}
                        </div>
                        <div className="flex items-center justify-between border-b border-border py-1">
                            <span className="text-muted-foreground">Shares</span>
                            <span>{holding.shares}</span>
                        </div>
                        <div className="flex items-center justify-between border-b border-border py-1">
                            <span className="text-muted-foreground">Cost Basis</span>
                            <span>{formatCurrencyUSD(holding.cost_basis)}</span>
                        </div>
                        <div className="flex items-center justify-between border-b border-border py-1">
                            <span className="text-muted-foreground">Total Gain/Loss</span>
                            <span className={holding.gain_loss >= 0 ? 'text-gain' : 'text-destructive'}>
                                {formatCurrencyUSD(holding.gain_loss)} ({holding.gain_loss_pct}%)
                            </span>
                        </div>
                        <div className="flex items-center justify-between py-1">
                            <span className="text-muted-foreground">Today's Gain/Loss</span>
                            <span className={holding.todays_gain_loss >= 0 ? 'text-gain' : 'text-destructive'}>
                                {formatCurrencyUSD(holding.todays_gain_loss)} ({holding.todays_gain_loss_pct}%)
                            </span>
                        </div>
                    </div>
                ) : (
                    <p className="flex-1 text-sm text-muted-foreground">
                        {ticker ? `You don't hold any shares of ${ticker}.` : 'No ticker selected.'}
                    </p>
                )}
                <div className="mt-3 flex gap-2">
                    <Button asChild className="flex-1">
                        <Link to={`/?group=transact&ticker=${encodeURIComponent(ticker)}`}>Transact</Link>
                    </Button>
                </div>
            </CardContent>
        </Card>
    )
}
