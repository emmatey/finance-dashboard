import { formatCurrencyUSD } from '@/scripts/utils';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function TradePostOrderSummary({
    orderSummaryData,
    viewController
}) {
    const { new_balance, qty, ticker, tx_value, unit_price } = orderSummaryData || {};

    function handleCloseSummary() {
        if (viewController) {
            viewController['setShowSummaryScreen'](false);
            viewController['setShowInput'](true);
        }
    }

    if (!orderSummaryData) {
        return (
            <Card>
                <CardContent>
                    <p className="text-sm text-muted-foreground">No order details available.</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="mx-auto max-w-md">
            <CardHeader>
                <CardTitle className="text-gain">Transaction Success</CardTitle>
            </CardHeader>

            <CardContent>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <h3 className="text-lg font-semibold">{ticker}</h3>
                        <p className="text-sm text-muted-foreground">Asset Traded</p>
                    </div>

                    <div>
                        <h3 className="text-lg font-semibold">{qty} shares</h3>
                        <p className="text-sm text-muted-foreground">Quantity Exchanged</p>
                    </div>

                    <div>
                        <h3 className="text-lg font-semibold">{formatCurrencyUSD(unit_price)}</h3>
                        <p className="text-sm text-muted-foreground">Execution Price (per unit)</p>
                    </div>

                    <div>
                        <h3 className="text-lg font-semibold">{formatCurrencyUSD(tx_value)}</h3>
                        <p className="text-sm text-muted-foreground">Total Transaction Value</p>
                    </div>

                    <div className="col-span-2">
                        <h3 className="text-lg font-semibold">{formatCurrencyUSD(new_balance)}</h3>
                        <p className="text-sm text-muted-foreground">Your New Remaining Balance</p>
                    </div>
                </div>
            </CardContent>

            <CardFooter>
                <Button type="button" onClick={handleCloseSummary}>Done</Button>
            </CardFooter>
        </Card>
    );
}