import usePortfolio from "./usePortfolio";
import useTransactionHistory from "../TransactionHistory/useTransactionHistory";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs } from "@/components/ui/tabs";
import PortfolioTable from "./PortfolioTable";
import TransactionHistoryShard from "../TransactionHistory/TransactionHistoryShard";


export default function PortfolioShard() {
    const { loading: portfolioLoading, data: portfolioData, error: portfolioError } = usePortfolio();

    const loading = portfolioLoading;
    const error = portfolioError;

    return (
        <div className='card'>
            {loading && (
                <span> Loading ... </span>
            )}

            {error && (
                <span> {error} </span>
            )}

            {!loading && !error && (
                <Tabs defaultValue="portfolio">
                    <PortfolioTable value="portfolio" data={portfolioData} />
                    <TransactionHistoryShard />
                </Tabs>
            )}
        </div>
    )
}