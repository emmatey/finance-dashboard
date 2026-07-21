import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { formatCurrencyUSD } from '@/scripts/utils'

function Stat({ label, value, valueClassName = '' }) {
    return (
        <div>
            <h3 className={`text-lg font-semibold ${valueClassName}`}>{value}</h3>
            <p className="text-sm text-muted-foreground">{label}</p>
        </div>
    );
}

export default function TradeHoldings({ tickerInfoJson }) {
    if (!tickerInfoJson || tickerInfoJson.error) {
        return (
            <Card className="flex min-h-45 items-center justify-center">
                <CardContent>
                    <p className="text-sm text-muted-foreground">Search a ticker to view your holdings.</p>
                </CardContent>
            </Card>
        );
    }

    const { qty_owned, holding_value, cash_balance } = tickerInfoJson;

    return (
        <Card>
            <CardHeader>
                <CardTitle>Your Position</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="flex flex-col gap-4">
                    <Stat label="Quantity Owned" value={`${qty_owned || 0} shares`} />
                    <Stat label="Current Value" value={formatCurrencyUSD(holding_value || 0)} />
                    <Separator />
                    <Stat label="Available Buying Power" value={formatCurrencyUSD(cash_balance || 0)} valueClassName="text-gain" />
                </div>
            </CardContent>
        </Card>
    );
}
