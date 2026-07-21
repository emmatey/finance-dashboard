import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Holdings from "./Holdings/Holdings";
import TransactionHistory from "./TransactionHistory/TransactionHistory";


export default function PortfolioShard() {
    return (
        <Card className="flex h-full min-h-0 flex-col">
            <CardContent className="flex h-full min-h-0 flex-1 flex-col">
                <Tabs defaultValue="portfolio" className="min-h-0 flex-1">
                    <TabsList>
                        <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
                        <TabsTrigger value="txHistory">Transaction History</TabsTrigger>
                    </TabsList>
                    <TabsContent value="portfolio" className="flex min-h-0 flex-1 flex-col">
                        <Holdings />
                    </TabsContent>
                    <TabsContent value="txHistory" className="flex min-h-0 flex-1 flex-col">
                        <TransactionHistory />
                    </TabsContent>
                </Tabs>
            </CardContent>
        </Card>
    )
}
