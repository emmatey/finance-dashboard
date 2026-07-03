import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { useMemo } from "react";
import { formatPercent, formatCurrencyUSD } from "@/scripts/utils";


export default function PortfolioTable({ data }) {
    const portfolioValue = useMemo(() => data.reduce((acc, cur) => acc + cur.current_value, 0),
        [data]
    );

    return (
        <div>
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
                    {data.map((row) => (
                        <TableRow key={row.symbol}>
                            <TableCell>
                                <h3>{row.symbol}</h3> <small>{row.name}</small>
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
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}
