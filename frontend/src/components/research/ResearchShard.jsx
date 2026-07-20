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
        <div className="container">
            <ResearchHeader quote={quote} financialMetrics={financialMetrics} />

            <hr className="mt-2" />

            <div className="row justify-content-center">
                <div className="col-md-8 mb-3">
                    <PriceChartCard prices={historicalPrices} />
                </div>
                <div className="col-md-4 mb-3">
                    <CompanyProfileCard profile={companyProfile} />
                </div>
            </div>

            <div className="row justify-content-center">
                <div className="col-md-8 mb-3">
                    <FinancialMetricsCard metrics={financialMetrics} />
                </div>
                <div className="col-md-4 mb-3">
                    <HoldingsCard />
                </div>
            </div>

            <div className="row justify-content-center">
                <div className="col-md-4 mb-3">
                    <AnalystSentimentCard financialMetrics={financialMetrics} quote={quote} />
                </div>
                <div className="col-md-4 mb-3">
                    <InsiderSentimentCard financialMetrics={financialMetrics} />
                </div>
                <div className="col-md-4 mb-3">
                    <StockSplitsCard stockSplits={stockSplits} />
                </div>
            </div>

            <div className="row justify-content-center">
                <div className="col-md-6 mb-3">
                    <NewsCard news={news} />
                </div>
                <div className="col-md-6 mb-3">
                    <InsiderTradesCard insiderTrades={insiderTrades} />
                </div>
            </div>
        </div>
    )
}
