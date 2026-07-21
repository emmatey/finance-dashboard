import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import TableSkeleton from '@/components/TableSkeleton'

export default function StockSplitsCard({ stockSplits, loading }) {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Stock Splits</CardTitle>
            </CardHeader>
            <CardContent>
                {loading ? (
                    <TableSkeleton columns={2} rows={4} />
                ) : stockSplits?.length > 0 ? (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Date</TableHead>
                                <TableHead>Ratio</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {stockSplits.map((s, i) => (
                                <TableRow key={i}>
                                    <TableCell>{s.split_date ?? 'N/A'}</TableCell>
                                    <TableCell>{s.split_ratio != null ? `${s.split_ratio}:1` : 'N/A'}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                ) : (
                    <p className="text-sm text-muted-foreground">No stock splits on record.</p>
                )}
            </CardContent>
        </Card>
    )
}
