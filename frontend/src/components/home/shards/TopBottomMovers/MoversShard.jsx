import TableSkeleton from "@/components/TableSkeleton";
import useHoldings from "../Portfolio/Holdings/useHoldings"
import MoversCard from "./MoversCard";
import { unsortedTestData, sortedTestData } from './testData.js'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from "@/components/ui/separator";
import { useMemo } from "react";



export default function MoversShard() {
    const { loading, data, error } = useHoldings();
    const sortedHoldings = useMemo(() => {
        if (!data) return;
        return [...data].sort((a, b) => {
            // on return value ... positive swap, negative don't swap, zero don't swap.
            if (Number(a.todays_gain_loss_pct) < Number(b.todays_gain_loss_pct)) {
                return 1;
            } else if ((Number(a.todays_gain_loss_pct) > Number(b.todays_gain_loss_pct))) {
                return -1;
            } else {
                return 0;
            };
        })
    }, [data]);

    let tops = [];
    let bottoms = [];
    if (sortedHoldings) {
        if (sortedHoldings.length >= 6) {
            tops = sortedHoldings.slice(0, 3);
            bottoms = sortedHoldings.slice(-3);
        } else {
            tops = sortedHoldings;
        };
    };

    return (
        <Card>
            {loading && <TableSkeleton />}
            {error && <CardTitle>{error}</CardTitle>}
            {!loading && !error && (
                <>
                    <CardHeader>
                        <CardTitle className="text-base font-bold">
                            Your top and bottom movers
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-[2fr_1fr_1fr] gap-4 px-2 pb-2 text-xs text-muted-foreground">
                            <small>Symbol</small>
                            <small className="text-right">Today's gain/loss</small>
                            <small className="text-right">Last Price</small>
                        </div>
                        {
                            tops && tops.map((company) => (
                                <MoversCard key={company.symbol} data={company}></MoversCard>
                            ))
                        }
                        {bottoms && <Separator />}
                        {
                            bottoms && bottoms.map((company) => (
                                <MoversCard key={company.symbol} data={company}></MoversCard>
                            ))
                        }
                    </CardContent>
                </>
            )}
        </Card>
    )
}