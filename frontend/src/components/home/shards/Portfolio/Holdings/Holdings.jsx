import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { useMemo } from "react";
import { Link } from "react-router-dom";
import { formatPercent, formatCurrencyUSD, getMarketStateBadge } from "@/scripts/utils";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import useHoldings from "./useHoldings";
import TableSkeleton from "../../../../TableSkeleton";


export default function Holdings({ username } = {}) {
    const { loading, data, error } = useHoldings(username);

    const portfolioValue = useMemo(
        () => (data ?? []).reduce((acc, cur) => acc + cur.current_value, 0),
        [data]
    );

    return (
        <div>
            {loading && (
                <TableSkeleton columns={8} />
            )}

            {error && (
                <span> {error} </span>
            )}

            {!loading && !error && (
                <ScrollArea className="h-80">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Symbol</TableHead>
                                <TableHead>Last Price</TableHead>
                                <TableHead>Today's gain/loss</TableHead>
                                <TableHead>Total gain/loss</TableHead>
                                <TableHead>Current Value</TableHead>
                                <TableHead>% of account</TableHead>
                                <TableHead>Quantity</TableHead>
                                <TableHead>Cost Basis</TableHead>
                            </TableRow>
                        </TableHeader>

                        <TableBody>
                            {data.map((row) => {
                                const marketStateBadge = getMarketStateBadge(row.market_state);
                                return (
                                <TableRow key={row.symbol}>
                                    <TableCell>
                                        <h3>
                                            <Link to={`/research?ticker=${encodeURIComponent(row.symbol)}`} className="hover:underline">
                                                {row.symbol}
                                            </Link>
                                            {' '}
                                            {marketStateBadge && (
                                                <Badge variant={marketStateBadge.variant}>{marketStateBadge.label}</Badge>
                                            )}
                                        </h3>
                                        <small>{row.name}</small>
                                    </TableCell>
                                    <TableCell>{formatCurrencyUSD(row.unit_price)}</TableCell>
                                    <TableCell>
                                        <h3>{formatCurrencyUSD(row.todays_gain_loss)}</h3> <small className={Number(row.todays_gain_loss_pct) > 0 ? 'text-gain' : 'text-destructive'}>{row.todays_gain_loss_pct}%</small>
                                    </TableCell>
                                    <TableCell>
                                        <h3>{formatCurrencyUSD(row.gain_loss)}</h3> <small className={Number(row.gain_loss_pct) > 0 ? 'text-gain' : 'text-destructive'}>{row.gain_loss_pct}%</small>
                                    </TableCell>
                                    <TableCell>{formatCurrencyUSD(row.current_value)}</TableCell>
                                    <TableCell>{formatPercent(row.current_value / portfolioValue)}</TableCell>
                                    <TableCell>{row.shares}</TableCell>
                                    <TableCell>{formatCurrencyUSD(row.cost_basis)}</TableCell>
                                </TableRow>
                                );
                            })}
                        </TableBody>
                    </Table>
                </ScrollArea>
            )}
        </div>
    )
}
