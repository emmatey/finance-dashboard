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

function gainLossClass(value) {
    return Number(value) > 0 ? 'text-gain' : 'text-destructive';
}

const columnDef = [
    {
        accessorKey: "ticker_plus_name",
        header: "Symbol",
        render: (row) => (
            <>
                <h3>{row.symbol}</h3> <small>{row.name}</small>
            </>
        ),
    },
    {
        accessorKey: "unit_price",
        header: "Last Price",
        render: (row) => formatCurrencyUSD(row.unit_price),
    },
    {
        accessorKey: "todays_gain_loss_plus_pct",
        header: "Today's gain/loss",
        render: (row) => (
            <>
                <h3>{formatCurrencyUSD(row.todays_gain_loss)}</h3> <small className={gainLossClass(row.todays_gain_loss)}>{row.todays_gain_loss_pct}%</small>
            </>
        ),
    },
    {
        accessorKey: "total_gain_loss_plus_pct",
        header: "Total gain/loss",
        render: (row) => (
            <>
                <h3>{formatCurrencyUSD(row.gain_loss)}</h3> <small className={gainLossClass(row.gain_loss)}>{row.gain_loss_pct}%</small>
            </>
        ),
    },
    {
        accessorKey: "current_value",
        header: "Current Value",
        render: (row) => formatCurrencyUSD(row.current_value),
    },
    {
        accessorKey: "pct_of_account",
        header: "% of account",
        render: (row, portfolioValue) => formatPercent(row.current_value / portfolioValue),
    },
    {
        accessorKey: "shares",
        header: "Quantity",
        render: (row) => row.shares,
    },
    {
        accessorKey: "cost_basis",
        header: "Cost Basis",
        render: (row) => formatCurrencyUSD(row.cost_basis),
    },
];

export default function PortfolioTable({ data }) {
    const rows = data ?? [];
    const portfolioValue = useMemo(
        () => rows.reduce((acc, cur) => acc + cur.current_value, 0),
        [rows]
    );

    return (
        <div>
            <Table>
                <TableHeader>
                    <TableRow>
                        {columnDef.map((colDef) => (
                            <TableHead key={colDef.accessorKey}>{colDef.header}</TableHead>
                        ))}
                    </TableRow>
                </TableHeader>

                <TableBody>
                    {rows.map((row) => (
                        <TableRow key={row.symbol}>
                            {columnDef.map((colDef) => (
                                <TableCell key={colDef.accessorKey}>
                                    {colDef.cell(row, portfolioValue)}
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}
