import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function HoldingsCard() {
    return (
        <Card className="flex h-full flex-col">
            <CardHeader>
                <CardTitle>Your Holdings</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-1 flex-col">
                <p className="flex-1 text-sm text-muted-foreground">Holdings data coming soon.</p>
                <div className="mt-3 flex gap-2">
                    <Button className="flex-1">Buy</Button>
                    <Button className="flex-1" variant="outline">Sell</Button>
                </div>
            </CardContent>
        </Card>
    )
}
