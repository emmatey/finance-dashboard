import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { formatNumber, formatCurrencyUSD } from '@/scripts/utils.js'

function getTransactionType(text) {
    /*
        Classifies a raw transactionText string into Buy/Sell/Other, mirroring the
        same 'Purchase at price'/'Sale at price' prefix match the backend uses to
        distinguish open-market trades from grants, option exercises, gifts, etc.
        (see StockScreenerManager.insider_trading_surge_screeners).
    */
    if (!text) return null
    if (text.startsWith('Purchase at price')) return 'Buy'
    if (text.startsWith('Sale at price')) return 'Sell'
    return 'Other'
}

function getTransactionTypeClass(type) {
    if (type === 'Buy') return 'border-gain/40 text-gain'
    if (type === 'Sell') return 'border-destructive/40 text-destructive'
    return ''
}

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
                                    {['Date', 'Filer', 'Relation', 'Type', 'Shares', 'Value', 'Description'].map(h => (
                                        <TableHead key={h}>{h}</TableHead>
                                    ))}
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {insiderTrades.map((t, i) => {
                                    const type = getTransactionType(t.transaction_text);
                                    return (
                                        <TableRow key={i}>
                                            <TableCell>{t.transaction_date ?? 'N/A'}</TableCell>
                                            <TableCell>{t.filer_name ?? 'N/A'}</TableCell>
                                            <TableCell>{t.filer_relation ?? 'N/A'}</TableCell>
                                            <TableCell>
                                                {type ? (
                                                    <Badge variant="outline" className={getTransactionTypeClass(type)}>
                                                        {type}
                                                    </Badge>
                                                ) : 'N/A'}
                                            </TableCell>
                                            <TableCell>{t.shares != null ? formatNumber(t.shares, 0) : 'N/A'}</TableCell>
                                            <TableCell>{formatCurrencyUSD(t.transaction_value)}</TableCell>
                                            <TableCell>{t.transaction_text ?? 'N/A'}</TableCell>
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                        <ScrollBar orientation="horizontal" />
                    </ScrollArea>
                ) : (
                    <p className="text-sm text-muted-foreground">No insider trades available.</p>
                )}
            </CardContent>
        </Card>
    )
}
