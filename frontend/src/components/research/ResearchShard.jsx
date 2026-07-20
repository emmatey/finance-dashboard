import ResearchHeader from "./researchCards/ResearchHeader";
import PriceChartCard from "./researchCards/PriceChartCard";
import CompanyProfileCard from "./researchCards/CompanyProfileCard";
import FinancialMetricsCard from "./researchCards/FinancialMetricsCard";
import HoldingsCard from "./researchCards/HoldingsCard";
import AnalystSentimentCard from "./researchCards/AnalystSentimentCard";
import InsiderSentimentCard from "./researchCards/InsiderSentimentCard";
import StockSplitsCard from "./researchCards/StockSplitsCard";
import NewsCard from "./researchCards/NewsCard";
import InsiderTradesCard from "./researchCards/InsiderTradesCard";
import useResearchData from "./useResearchData"

export default function ResearchShard({ ticker }) {
    const { data } = useResearchData(ticker);
    const {
        symbols: quote,
        company_profile: companyProfile,
        financial_metrics: financialMetrics,
        historical_prices: historicalPrices,
        insider_trades: insiderTrades,
        news,
        stock_splits: stockSplits
    } = data || {};

    return (
        <div className="mx-auto max-w-6xl space-y-4 p-4">
            <ResearchHeader quote={quote} financialMetrics={financialMetrics} />

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
                <div className="lg:col-span-2">
                    <PriceChartCard prices={historicalPrices} />
                </div>
                <CompanyProfileCard profile={companyProfile} />
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
                <div className="lg:col-span-2">
                    <FinancialMetricsCard metrics={financialMetrics} />
                </div>
                <HoldingsCard />
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <AnalystSentimentCard financialMetrics={financialMetrics} quote={quote} />
                <InsiderSentimentCard financialMetrics={financialMetrics} />
                <StockSplitsCard stockSplits={stockSplits} />
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <NewsCard news={news} />
                <InsiderTradesCard insiderTrades={insiderTrades} />
            </div>
        </div>
    )
}
