import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Holdings from "./Holdings/Holdings";
import TransactionHistory from "./TransactionHistory/TransactionHistory";


export default function PortfolioShard() {
    return (
        <div className='card'>
            <Tabs defaultValue="portfolio">
                <TabsList>
                    <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
                    <TabsTrigger value="txHistory">Transaction History</TabsTrigger>
                </TabsList>
                <TabsContent value="portfolio"><Holdings /></TabsContent>
                <TabsContent value="txHistory"><TransactionHistory /></TabsContent>
            </Tabs>
        </div>
    )
}