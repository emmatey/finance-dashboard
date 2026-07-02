import usePortfolio from "./usePortfolio";
import useTransactionHistory from "../TransactionHistory/useTransactionHistory";
import { Skeleton } from "@/components/ui/skeleton";
import PortfolioTable from "./PortfolioTable";


export default function PortfolioShard() {
    const { loading: portfolioLoading, data: portfolioData, error: portfolioError } = usePortfolio();
    const { loading: txLoading, data: txData, error: txError } = useTransactionHistory();

    const loading = portfolioLoading || txLoading;

    return (
        <div className='card'>
            {loading && (
                <span> Loading ... </span>
            )}
            {!loading && (
                <PortfolioTable data={portfolioData}/>
            )}
        </div>
    )
}