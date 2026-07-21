import { parseResponse, formatCurrencyUSD } from '@/scripts/utils';
import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

export default function TradeOrderConfirm({
    pendingOrder,
    tickerInfoJson,
    setActiveQuery,
    setOrderSummaryData,
    viewController
}) {
    const [isError, setIsError] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { txTicker, txType, txShareQty, txDollarQty } = pendingOrder;

    async function handleSubmitTradeOrder(event) {
        event.preventDefault();
        setIsSubmitting(true);
        
        try {
            const res = await fetch("/api/trade", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    'ticker': txTicker,
                    'qty': txShareQty,
                    'transaction_type': txType
                })
            });

            const statusJson = await parseResponse(res);

            viewController['setShowConfirmationScreen'](false);
            viewController['setShowSummaryScreen'](true);
            setActiveQuery(null);
            setOrderSummaryData(statusJson);
        } catch (error) {
            setIsError(error.message || "An unexpected error occurred.");
        } finally {
            setIsSubmitting(false);
        }
    }

    function handleCancelTx() {
        setActiveQuery(null);
        viewController['setShowConfirmationScreen'](false);
        viewController['setShowInput'](true);
    }

    return (
        <Card>
            <form onSubmit={handleSubmitTradeOrder} className="contents">
                <CardHeader>
                    <CardTitle>{isError ? "Transaction Failed" : "Confirm Your Transaction"}</CardTitle>
                </CardHeader>
                <Separator />
                <CardContent>
                    {isError ? (
                        <div className="py-4 text-center">
                            <p className="font-semibold text-destructive">{isError}</p>
                            <p className="mt-2 text-sm text-muted-foreground">
                                Please return to the input screen to adjust your order parameters.
                            </p>
                        </div>
                    ) : (
                        <div className="flex flex-col gap-4">
                            <div>
                                <h3 className="text-lg font-semibold">{txTicker}</h3>
                                <p className="text-sm text-muted-foreground">Company being traded</p>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold uppercase">{txType}</h3>
                                <p className="text-sm text-muted-foreground">Transaction type</p>
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold">
                                    {txShareQty} shares for a total value of {formatCurrencyUSD(txDollarQty)}
                                </h3>
                                <p className="text-sm text-muted-foreground">
                                    Price was last updated at {tickerInfoJson?.last_updated} UTC
                                </p>
                            </div>
                        </div>
                    )}
                </CardContent>

                <CardFooter className="gap-2">
                    <Button type="submit" disabled={isSubmitting || isError}>
                        {isSubmitting ? "Processing..." : "Submit Transaction"}
                    </Button>
                    <Button type="button" variant="outline" onClick={handleCancelTx}>
                        {isError ? "Back to Input" : "Cancel Transaction"}
                    </Button>
                </CardFooter>
            </form>
        </Card>
    );
}
