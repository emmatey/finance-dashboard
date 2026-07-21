import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import TradeSearch from './TradeInput/TradeSearch.jsx';
import TradeOrderForm from './TradeInput/TradeOrderForm.jsx';
import TradeHoldings from './TradeInput/TradeHoldings.jsx';
import TradeMarketData from './TradeInput/TradeMarketData.jsx';

export default function TradeInput({
    activeQuery,
    setActiveQuery,
    loading,
    tickerInfoJson,
    setPendingOrder,
    viewController
}) {
    return (
        <div className="grid grid-cols-1 items-start gap-4 lg:grid-cols-3">
            <Card className="z-10 lg:col-span-1">
                <CardContent>
                    <TradeSearch
                        activeQuery={activeQuery}
                        setActiveQuery={setActiveQuery}
                        loading={loading}
                        tickerInfoJson={tickerInfoJson}
                    />
                    <Separator className="my-4" />
                    <TradeMarketData
                        activeQuery={activeQuery}
                        loading={loading}
                        tickerInfoJson={tickerInfoJson}
                    />
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Place Order</CardTitle>
                </CardHeader>
                <CardContent>
                    <TradeOrderForm
                        tickerInfoJson={tickerInfoJson}
                        setPendingOrder={setPendingOrder}
                        viewController={viewController}
                    />
                </CardContent>
            </Card>

            <TradeHoldings tickerInfoJson={tickerInfoJson} />
        </div>
    );
}