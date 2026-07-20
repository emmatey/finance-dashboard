import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ScrollArea } from '@/components/ui/scroll-area'
import { formatNumber, formatCurrencyUSD } from '@/scripts/utils.js'

export default function InsiderTradesCard({ insiderTrades }) {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Insider Trades</CardTitle>
            </CardHeader>
            <CardContent>
                {insiderTrades?.length > 0 ? (
                    <ScrollArea className="h-80">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    {['Date', 'Filer', 'Relation', 'Shares', 'Value', 'Transaction'].map(h => (
                                        <TableHead key={h}>{h}</TableHead>
                                    ))}
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {insiderTrades.map((t, i) => (
                                    <TableRow key={i}>
                                        <TableCell>{t.transaction_date ?? 'N/A'}</TableCell>
                                        <TableCell>{t.filer_name ?? 'N/A'}</TableCell>
                                        <TableCell>{t.filer_relation ?? 'N/A'}</TableCell>
                                        <TableCell>{t.shares != null ? formatNumber(t.shares, 0) : 'N/A'}</TableCell>
                                        <TableCell>{formatCurrencyUSD(t.transaction_value)}</TableCell>
                                        <TableCell>{t.transaction_text ?? 'N/A'}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </ScrollArea>
                ) : (
                    <p className="text-sm text-muted-foreground">No insider trades available.</p>
                )}
            </CardContent>
        </Card>
    )
}
