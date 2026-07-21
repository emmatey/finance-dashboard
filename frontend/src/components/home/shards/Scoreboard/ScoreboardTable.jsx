import { Link } from "react-router-dom";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { formatCurrencyUSD } from "@/scripts/utils";
import { ScrollArea } from "@/components/ui/scroll-area";


export default function ScoreboardTable({ data }) {
    // data: [{
    //     username: str,
    //     snap_datetime: str,
    //     portfolio_value: float,
    //     cash_balance: float,
    //     grand_total: float,
    //     rank: int
    // }]
    return (
        <ScrollArea className="h-80">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Rank</TableHead>
                        <TableHead>Username</TableHead>
                        <TableHead>Portfolio Value</TableHead>
                        <TableHead>Cash Balance</TableHead>
                        <TableHead>Total</TableHead>
                    </TableRow>
                </TableHeader>

                <TableBody>
                    {data.map((row) => (
                        <TableRow key={row.username}>
                            <TableCell>{row.rank}</TableCell>
                            <TableCell>
                                <Link to={`/user/${row.username}`} className="hover:underline">
                                    {row.username}
                                </Link>
                            </TableCell>
                            <TableCell>{formatCurrencyUSD(row.portfolio_value)}</TableCell>
                            <TableCell>{formatCurrencyUSD(row.cash_balance)}</TableCell>
                            <TableCell>{formatCurrencyUSD(row.grand_total)}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </ScrollArea>
    )
}
