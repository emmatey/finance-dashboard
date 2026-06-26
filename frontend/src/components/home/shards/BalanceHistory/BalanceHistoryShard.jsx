import { Card, CardContent } from '@/components/ui/card.jsx'
import useBalanceHistory from './useBalanceHistory'
import BalanceHistoryChart from './BalanceHistoryChart.jsx'

export default function BalanceHistoryShard() {
    const { loading, data, error } = useBalanceHistory()

    if (loading) return <div>Loading...</div>
    if (error) return <p className="text-sm text-destructive">{error}</p>

    const snapshots = data?.data ?? []
    if (!snapshots.length) return null

    return (
        <Card className="w-full">
            <CardContent className="p-6">
                <p className="text-sm font-medium mb-4">Account History</p>
                <BalanceHistoryChart snapshots={snapshots} />
            </CardContent>
        </Card>
    )
}
