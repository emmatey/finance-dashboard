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
import { formatCurrencyUSD } from "@/scripts/utils";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import useTransactionHistory from './useTransactionHistory.js'
import TableSkeleton from '../../../../TableSkeleton.jsx'


export default function TransactionHistory() {
    const { loading, data, error } = useTransactionHistory();
    // add server side pagination later.

    const transactions = useMemo(
        () => [...(data ?? [])].sort((a, b) => new Date(b.datetime) - new Date(a.datetime)),
        [data]
    );

    return (
        <div>
            {loading && (
                <TableSkeleton columns={6} />
            )}

            {error && (
                <span> {error} </span>
            )}

            {!loading && !error && (
                <ScrollArea className="h-80">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Type</TableHead>
                                <TableHead>Ticker</TableHead>
                                <TableHead>Qty</TableHead>
                                <TableHead>Price/Share</TableHead>
                                <TableHead>Date</TableHead>
                                <TableHead>Balance After</TableHead>
                            </TableRow>
                        </TableHeader>

                        <TableBody>
                            {transactions.map((tx) => (
                                <TableRow key={tx.transaction_id}>
                                    <TableCell>
                                        <Badge variant={tx.transaction_type === 'buy' ? 'default' : 'secondary'}>
                                            {String(tx.transaction_type).toLocaleUpperCase()}
                                        </Badge>
                                    </TableCell>
                                    <TableCell>
                                        {tx.ticker !== 'CASH' ? (
                                            <Link to={`/research?ticker=${encodeURIComponent(tx.ticker)}`} className="hover:underline">
                                                {tx.ticker}
                                            </Link>
                                        ) : (
                                            tx.ticker
                                        )}
                                    </TableCell>
                                    <TableCell>{Math.abs(tx.qty)}</TableCell>
                                    <TableCell>{formatCurrencyUSD(tx.unit_price)}</TableCell>
                                    <TableCell>{tx.datetime}</TableCell>
                                    <TableCell>{formatCurrencyUSD(tx.cash_after)}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </ScrollArea>
            )}
        </div>
    )
}
