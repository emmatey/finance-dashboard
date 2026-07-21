import { Link } from "react-router-dom";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { formatCurrencyUSD, formatNumber } from "@/scripts/utils";

export default function ScreenersTable({ data }) {
    //from - {
    //screener_name: [{
    //    screener_name: str,
    //    rank: int,
    //    ticker: str,
    //    company_name: str,
    //    current_price: float,
    //    prev_close: float,
    //    price_change_pct: float,
    //    market_cap: float,
    //    todays_volume: int,
    //    three_month_avg_volume: int,
    //    volume_change_pct: float
    //}]
    return (
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead>Ticker</TableHead>
                    <TableHead>Company</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Prev Close</TableHead>
                    <TableHead>Change</TableHead>
                    <TableHead>Market Cap</TableHead>
                    <TableHead>Today's Volume</TableHead>
                    <TableHead>3mo Avg Volume</TableHead>
                    <TableHead>Volume Change</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {data.map((row) => (
                    <TableRow key={row.ticker}>
                        <TableCell>
                            <Link to={`/research?ticker=${encodeURIComponent(row.ticker)}`} className="hover:underline">
                                {row.ticker}
                            </Link>
                        </TableCell>
                        <TableCell>{row.company_name}</TableCell>
                        <TableCell>{formatCurrencyUSD(row.current_price)}</TableCell>
                        <TableCell>{formatCurrencyUSD(row.prev_close)}</TableCell>
                        <TableCell className={row.price_change_pct > 0 ? 'text-gain' : 'text-destructive'}>
                            {row.price_change_pct}%
                        </TableCell>
                        <TableCell>{formatCurrencyUSD(row.market_cap)}</TableCell>
                        <TableCell>{formatNumber(row.todays_volume, 0)}</TableCell>
                        <TableCell>{formatNumber(row.three_month_avg_volume, 0)}</TableCell>
                        <TableCell className={row.volume_change_pct > 0 ? 'text-gain' : 'text-destructive'}>
                            {row.volume_change_pct}%
                        </TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    )
}
