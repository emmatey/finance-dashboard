import { useEffect, useState } from 'react'
import { unpackFetchResponse } from '../scripts/utils.js'
import ResearchHeader from './researchBody/ResearchHeader.jsx'
import PriceChart from './PriceChart.jsx'
import HoldingsCard from './researchBody/HoldingsCard.jsx'
import CompanyProfileCard from './researchBody/CompanyProfileCard.jsx'
import FinancialMetricsCard from './researchBody/FinancialMetricsCard.jsx'
import AnalystSentimentCard from './researchBody/AnalystSentimentCard.jsx'
import InsiderSentimentCard from './researchBody/InsiderSentimentCard.jsx'
import NewsCard from './researchBody/NewsCard.jsx'
import InsiderTradesCard from './researchBody/InsiderTradesCard.jsx'
import StockSplitsCard from './researchBody/StockSplitsCard.jsx'

export default function ResearchBody({ ticker }) {
    const [data, setData] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!ticker) return
        setData(null)
        setError(null)

        let cancelled = false

        async function load() {
            try {
                const localRes = await fetch(`/api/research/local?ticker=${ticker}`)
                const local = await unpackFetchResponse(localRes)
                if (!cancelled) setData(local)
            } catch {
                // ticker may not be in DB yet — continue to online
            }

            try {
                const onlineRes = await fetch(`/api/research/online?ticker=${ticker}`)
                const online = await unpackFetchResponse(onlineRes)
                if (!cancelled) setData(online)
            } catch (err) {
                if (!cancelled) setError(err.message)
            }
        }

        load()
        return () => { cancelled = true }
    }, [ticker])

    if (!ticker) return <main className="container py-4"><h2>Research</h2><p>Search for a company to view research.</p></main>
    if (error && !data) return <main className="container py-4"><h2>Research: {ticker}</h2><p className="text-danger">{error}</p></main>
    if (!data) return <main className="container py-4"><h2>Research: {ticker}</h2><p className="text-muted">Loading…</p></main>

    const symbol = data.symbols?.[0]
    const profile = data.company_profile?.[0]
    const metrics = data.financial_metrics?.[0]
    const prices = data.historical_prices ?? []
    const news = data.news ?? []
    const insiderTrades = data.insider_trades ?? []
    const stockSplits = data.stock_splits ?? []

    const lastPrice = symbol?.last_price
    const analystUpside = lastPrice && metrics?.target_price
        ? ((metrics.target_price - lastPrice) / lastPrice) * 100
        : null

    return (
        <main className="container py-3">

            <ResearchHeader
                ticker={ticker}
                companyName={symbol?.company_name ?? ticker}
                exchange={symbol?.exchange}
                quoteType={symbol?.quote_type}
                lastPrice={lastPrice}
                metrics={metrics}
            />

            <hr className="mt-1 mb-3" />

            {/* Row 1: Price chart + Holdings */}
            <div className="row mb-3">
                <div className="col-md-9">
                    <div className="card h-100">
                        <div className="card-body">
                            <PriceChart prices={prices} />
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <HoldingsCard />
                </div>
            </div>

            {/* Row 2: Company profile + Financial metrics */}
            <div className="row mb-3">
                <div className="col-md-4">
                    <CompanyProfileCard profile={profile} />
                </div>
                <div className="col-md-8">
                    <FinancialMetricsCard metrics={metrics} />
                </div>
            </div>

            {/* Row 3: Analyst sentiment + Insider sentiment */}
            <div className="row mb-3">
                <div className="col-md-6">
                    <AnalystSentimentCard metrics={metrics} lastPrice={lastPrice} analystUpside={analystUpside} />
                </div>
                <div className="col-md-6">
                    <InsiderSentimentCard metrics={metrics} />
                </div>
            </div>

            {/* Row 4: News + Insider trades */}
            <div className="row mb-3">
                <div className="col-md-6">
                    <NewsCard news={news} />
                </div>
                <div className="col-md-6">
                    <InsiderTradesCard insiderTrades={insiderTrades} />
                </div>
            </div>

            {/* Row 5: Stock splits (only if data exists) */}
            <StockSplitsCard stockSplits={stockSplits} />

        </main>
    )
}
