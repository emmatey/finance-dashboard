import { Card, CardContent } from '@/components/ui/card.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { formatCurrencyUSD } from '@/scripts/utils.js'
import useUserSummary from './useUserSummary'

export default function UserSummaryShard() {
    const { loading, data, error, responseCode } = useUserSummary();

    if (loading) return <div>Loading...</div>;
    if (error) return <p className="text-sm text-destructive">{error}</p>;
    if (!data) return null;

    const lastUpdated = data.snap_datetime
        ? new Date(data.snap_datetime).toLocaleString()
        : null;

    return (
        <Card >

        </Card>
    );
}
