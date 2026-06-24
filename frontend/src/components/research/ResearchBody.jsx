import { useEffect, useRef, useState } from 'react'
import {
    formatCurrencyUSD,
    formatPercent,
    formatNumber,
    formatLargeNumber,
    formatAnalystRating,
    getAnalystRatingColorClass,
    getSentimentLabel,
    getSentimentColorClass,
} from '@/scripts/utils.js'
import useResearchData from './useResearchData.js'

const RANGES = { '1yr': 31536000, '1mo': 2592000, '1wk': 604800 }

function SentimentBar({ score }) {
    if (score == null) return <p className="text-muted small mb-0">No data available.</p>
    const position = Math.max(0, Math.min(100, ((score + 1) / 2) * 100))
    return (
        <div className="mt-2">
            <div style={{ 
                position: 'relative', 
                height: '8px', 
                borderRadius: '4px', 
                background: 'linear-gradient(to right, var(--color-loss), var(--color-border) 50%, var(--color-gain))'
                 }}>
                <div style={{ 
                    position: 'absolute', 
                    left: `${position}%`, 
                    top: '-4px', 
                    transform: 'translateX(-50%)', 
                    width: '3px', 
                    height: '16px', 
                    background: '#333', 
                    borderRadius: '2px' 
                    }} />
            </div>
            <div className="d-flex justify-content-between mt-1 small">
                <span className="text-muted">Bearish</span>
                <span className="text-muted">Neutral</span>
                <span className="text-muted">Bullish</span>
            </div>
        </div>
    )
}

function getSubsetIdx(timestamps, timeDelta) {
    const now = Math.floor(Date.now() / 1000)
    const target = now - timeDelta
    for (const [idx, ts] of timestamps.entries()) {
        if (ts >= target) return idx
    }
    return timestamps.length
}

function PriceChart({ prices }) {
    const canvasRef = useRef(null)
    const chartRef = useRef(null)
    const [range, setRange] = useState('1yr')

    const sorted = prices?.length
        ? [...prices].sort((a, b) => a.timestamp - b.timestamp)
        : []

    useEffect(() => {
        if (!sorted.length || !canvasRef.current) return

        const Chart = window.Chart
        if (!Chart) return

        const idx = getSubsetIdx(sorted.map(p => p.timestamp), RANGES[range])
        const data = sorted.slice(idx).length > 0 ? sorted.slice(idx) : sorted

        const labels = data.map(d => new Date(d.timestamp * 1000).toLocaleDateString())
        const openPrices = data.map(d => d.price)
        const volumes = data.map(d => d.volume)
        const isGain = openPrices[openPrices.length - 1] >= openPrices[0]
        const lineColor = isGain ? '#16A34A' : '#FF534C'

        if (chartRef.current) chartRef.current.destroy()

        chartRef.current = new Chart(canvasRef.current, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Open Price',
                    data: openPrices,
                    borderColor: lineColor,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: `Open Price — ${range}` },
                    legend: { display: false },
                    tooltip: {
                        displayColors: false,
                        callbacks: {
                            label: ctx => {
                                const price = Number(ctx.parsed.y).toLocaleString('en-US', { style: 'currency', currency: 'USD' })
                                return `Open: ${price}`
                            },
                            afterBody: ctx => {
                                const vol = volumes[ctx[0].dataIndex]
                                return vol != null ? `Volume: ${Number(vol).toLocaleString()}` : ''
                            }
                        }
                    }
                },
                scales: {
                    x: { ticks: { maxTicksLimit: 8 } },
                    y: { ticks: { callback: v => '$' + Number(v).toLocaleString() } }
                }
            }
        })

        return () => {
            chartRef.current?.destroy()
            chartRef.current = null
        }
    }, [sorted, range])

    if (!prices?.length) return <p className="text-muted small mb-0">No price history available.</p>

    return (
        <>
            <canvas ref={canvasRef} />
            <div className="d-flex justify-content-center gap-2 mt-2">
                {Object.keys(RANGES).map(r => (
                    <button key={r} onClick={() => setRange(r)}
                        className={`btn btn-sm ${range === r ? 'btn-primary' : 'btn-outline-secondary'}`}>
                        {r}
                    </button>
                ))}
            </div>
        </>
    )
}

export default function ResearchBody({ ticker }) {
    const { data, errorStatus } = useResearchData(ticker)

    const errorMessages = {
        404: 'Ticker not found.',
        500: 'Something went wrong. Please try again.',
    }

    if (!ticker) return <main className="container py-4"><h2>Research</h2><p>Search for a company to view research.</p></main>
    if (errorStatus && !data) return <main className="container py-4"><h2>Research: {ticker}</h2><p className="text-danger">{errorMessages[errorStatus] ?? 'Unable to reach the server.'}</p></main>
    if (!data) return <main className="container py-4"><h2>Research: {ticker}</h2><p className="text-muted">Loading…</p></main>

    const symbol = data.symbols?.[0]
    const profile = data.company_profile?.[0]
    const metrics = data.financial_metrics?.[0]
    const prices = data.historical_prices ?? []
    const news = data.news ?? []
    const insiderTrades = data.insider_trades ?? []
    const stockSplits = data.stock_splits ?? []

    const companyName = symbol?.company_name ?? ticker
    const lastPrice = symbol?.last_price
    const exchange = symbol?.exchange
    const quoteType = symbol?.quote_type

    const analystUpside = lastPrice && metrics?.target_price
        ? ((metrics.target_price - lastPrice) / lastPrice) * 100
        : null

    return (
        <main className="container py-3">

            {/* Header */}
            <div className="d-flex justify-content-between align-items-end mb-2">
                <div>
                    <div className="lh-sm mb-1">
                        <span className="fw-bold fs-5">{ticker}</span>
                        <span className="text-muted ms-2">
                            {companyName}
                            {exchange ? ` · ${exchange}` : ''}
                            {quoteType ? ` · ${quoteType}` : ''}
                        </span>
                    </div>
                    <div className="d-flex align-items-baseline gap-3">
                        <span className="fw-bold fs-3">{lastPrice != null ? formatCurrencyUSD(lastPrice) : '—'}</span>
                        {metrics && (
                            <span className="text-muted small">
                                Open {formatCurrencyUSD(metrics.market_open)}
                                <span className="mx-2">·</span>
                                Prev Close {formatCurrencyUSD(metrics.prev_close)}
                            </span>
                        )}
                    </div>
                </div>
                <div className="d-flex gap-2">
                    <button className="btn btn-primary">Buy</button>
                    <button className="btn btn-primary">Sell</button>
                </div>
            </div>

            <hr className="mt-1 mb-3" />

            {/* Row 1: Price chart (col-9) + Holdings (col-3) */}
            <div className="row mb-3">
                <div className="col-md-9">
                    <div className="card h-100">
                        <div className="card-body">
                            <PriceChart prices={prices} />
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card h-100">
                        <div className="card-body d-flex flex-column">
                            <h5 className="card-title">Your Holdings</h5>
                            <p className="text-muted small mb-0 flex-grow-1">Holdings data coming soon.</p>
                            <div className="d-flex gap-2 mt-3">
                                <button className="btn btn-primary flex-grow-1">Buy</button>
                                <button className="btn btn-primary flex-grow-1">Sell</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Row 2: Company profile (col-4) + Financial metrics (col-8) */}
            <div className="row mb-3">
                <div className="col-md-4">
                    <div className="card h-100">
                        <div className="card-body">
                            <h5 className="card-title">Company Profile</h5>
                            {profile ? (
                                <>
                                    <p className="small overflow-auto" style={{ maxHeight: '170px' }}>{profile.company_desc ?? 'No description available.'}</p>
                                    <table className="table table-sm mb-0">
                                        <tbody>
                                            {[
                                                ['Sector', profile.sector],
                                                ['Industry', profile.industry],
                                                ['Employees', profile.employee_count != null ? formatNumber(profile.employee_count, 0) : null],
                                                ['Website', profile.website
                                                    ? <a href={profile.website} target="_blank" rel="noreferrer">{profile.website}</a>
                                                    : null],
                                            ].map(([label, value]) => (
                                                <tr key={label}>
                                                    <th className="text-muted fw-normal small" style={{ width: '40%' }}>{label}</th>
                                                    <td className="small">{value ?? 'N/A'}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </>
                            ) : (
                                <p className="text-muted small mb-0">Loading…</p>
                            )}
                        </div>
                    </div>
                </div>

                <div className="col-md-8">
                    <div className="card h-100">
                        <div className="card-body">
                            <h5 className="card-title">Financial Metrics</h5>
                            {metrics ? (
                                <div className="row row-cols-3 g-2">
                                    {[
                                        ['Market Cap', formatLargeNumber(metrics.market_cap)],
                                        ['EPS', formatCurrencyUSD(metrics.eps)],
                                        ['Beta', formatNumber(metrics.beta)],
                                        ['Trailing P/E', formatNumber(metrics.trailing_pe)],
                                        ['Forward P/E', formatNumber(metrics.forward_pe)],
                                        ['Profit Margin', formatPercent(metrics.profit_margin)],
                                        ['Dividend Yield', formatPercent(metrics.dividend_yield)],
                                        ['52-wk High', formatCurrencyUSD(metrics.fifty_two_week_high)],
                                        ['52-wk Low', formatCurrencyUSD(metrics.fifty_two_week_low)],
                                        ['50-day Avg', formatCurrencyUSD(metrics.fifty_day_average)],
                                        ['200-day Avg', formatCurrencyUSD(metrics.two_hundred_day_average)],
                                        ['Price / Book', formatNumber(metrics.price_to_book)],
                                        ['Book Value', formatCurrencyUSD(metrics.book_value)],
                                        ['Shares Out.', formatLargeNumber(metrics.shares_outstanding)],
                                        ['Current Ratio', formatNumber(metrics.current_ratio)],
                                        ['Debt / Equity', formatNumber(metrics.debt_to_equity)],
                                        ["Today's Vol.", formatLargeNumber(metrics.todays_volume)],
                                        ['10-day Avg Vol', formatLargeNumber(metrics.ten_day_avg_volume)],
                                        ['3-mo Avg Vol', formatLargeNumber(metrics.three_month_avg_volume)],
                                    ].map(([label, value]) => (
                                        <div key={label} className="col border-bottom pb-1">
                                            <div className="text-muted">{label}</div>
                                            <div className="fw-semibold small">{value}</div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-muted small mb-0">Loading…</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Row 3: Analyst sentiment + Insider sentiment */}
            <div className="row mb-3">
                <div className="col-md-6">
                    <div className="card h-100">
                        <div className="card-body">
                            <h5 className="card-title">Analyst Sentiment</h5>
                            {metrics ? (
                                <>
                                    <div className="mb-3">
                                        <span className={`fw-bold fs-4 ${getAnalystRatingColorClass(metrics.rating)}`}>
                                            {formatAnalystRating(metrics.rating)}
                                        </span>
                                        {metrics.analyst_count != null && (
                                            <span className="text-muted small ms-2">
                                                {metrics.analyst_count} analyst{metrics.analyst_count !== 1 ? 's' : ''}
                                            </span>
                                        )}
                                    </div>
                                    <table className="table table-sm mb-0">
                                        <tbody>
                                            <tr>
                                                <th className="text-muted fw-normal small">Target Price</th>
                                                <td className="small">{formatCurrencyUSD(metrics.target_price)}</td>
                                            </tr>
                                            <tr>
                                                <th className="text-muted fw-normal small">Current Price</th>
                                                <td className="small">{formatCurrencyUSD(lastPrice)}</td>
                                            </tr>
                                            {analystUpside != null && (
                                                <tr>
                                                    <th className="text-muted fw-normal small">
                                                        <span title="How much the current price would need to move to reach the analyst consensus target. Positive = analysts expect growth, negative = analysts expect a decline.">
                                                            Implied Upside ⓘ
                                                        </span>
                                                    </th>
                                                    <td className={`small fw-semibold ${analystUpside >= 0 ? 'text-success' : 'text-danger'}`}>
                                                        {analystUpside >= 0 ? '+' : ''}{analystUpside.toFixed(1)}%
                                                    </td>
                                                </tr>
                                            )}
                                        </tbody>
                                    </table>
                                </>
                            ) : (
                                <p className="text-muted small mb-0">Loading…</p>
                            )}
                        </div>
                    </div>
                </div>

                <div className="col-md-6">
                    <div className="card h-100">
                        <div className="card-body">
                            <h5 className="card-title">Insider Sentiment</h5>
                            {metrics ? (
                                <>
                                    <div className="mb-2">
                                        <span className={`fw-bold fs-4 ${getSentimentColorClass(metrics.insider_sentiment)}`}>
                                            {getSentimentLabel(metrics.insider_sentiment)}
                                        </span>
                                        {metrics.insider_sentiment != null && (
                                            <span className="text-muted small ms-2">
                                                score: {Number(metrics.insider_sentiment).toFixed(3)}
                                            </span>
                                        )}
                                    </div>
                                    <SentimentBar score={metrics.insider_sentiment} />
                                    <p className="text-muted small mt-2 mb-0">
                                        Based on open-market insider trades in the past 12 months. Buys are weighted over sells.
                                    </p>
                                </>
                            ) : (
                                <p className="text-muted small mb-0">Loading…</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Row 4: News + Insider trades */}
            <div className="row mb-3">
                <div className="col-md-6">
                    <div className="card h-100">
                        <div className="card-body">
                            <h5 className="card-title">News</h5>
                            {news.length > 0 ? (
                                <ul className="list-unstyled mb-0 overflow-auto" style={{ maxHeight: '400px' }}>
                                    {news.map((n, i) => (
                                        <li key={n.uuid ?? i} className="d-flex gap-2 align-items-start py-2 border-bottom">
                                            {n.thumbnail && (
                                                <img src={n.thumbnail} alt="" className="object-fit-cover rounded-1 flex-shrink-0" style={{ width: '64px', height: '42px' }} />
                                            )}
                                            <div>
                                                <a href={n.link} target="_blank" rel="noreferrer" className="fw-semibold small d-block mb-1">
                                                    {n.title}
                                                </a>
                                                <span className="text-muted small">
                                                    {n.publisher}
                                                    {n.providerPublishTime ? ` · ${new Date(n.providerPublishTime * 1000).toLocaleDateString()}` : ''}
                                                </span>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="text-muted small mb-0">No news available.</p>
                            )}
                        </div>
                    </div>
                </div>

                <div className="col-md-6">
                    <div className="card h-100">
                        <div className="card-body">
                            <h5 className="card-title">Insider Trades</h5>
                            {insiderTrades.length > 0 ? (
                                <div className="table-responsive overflow-auto" style={{ maxHeight: '400px' }}>
                                    <table className="table table-sm mb-0">
                                        <thead>
                                            <tr>
                                                {['Date', 'Filer', 'Relation', 'Shares', 'Value', 'Transaction'].map(h => (
                                                    <th key={h} className="text-muted fw-normal small">{h}</th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {insiderTrades.map((t, i) => (
                                                <tr key={i}>
                                                    <td className="small">{t.transaction_date ?? 'N/A'}</td>
                                                    <td className="small">{t.filer_name ?? 'N/A'}</td>
                                                    <td className="small">{t.filer_relation ?? 'N/A'}</td>
                                                    <td className="small">{t.shares != null ? formatNumber(t.shares, 0) : 'N/A'}</td>
                                                    <td className="small">{formatCurrencyUSD(t.transaction_value)}</td>
                                                    <td className="small">{t.transaction_text ?? 'N/A'}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <p className="text-muted small mb-0">No insider trades available.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Row 5: Stock splits (only if data exists) */}
            {stockSplits.length > 0 && (
                <div className="row mb-3">
                    <div className="col-12">
                        <div className="card">
                            <div className="card-body">
                                <h5 className="card-title">Stock Splits</h5>
                                <table className="table table-sm mb-0">
                                    <thead>
                                        <tr>
                                            <th className="text-muted fw-normal small">Date</th>
                                            <th className="text-muted fw-normal small">Ratio</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {stockSplits.map((s, i) => (
                                            <tr key={i}>
                                                <td className="small">{s.split_date ?? 'N/A'}</td>
                                                <td className="small">{s.split_ratio != null ? `${s.split_ratio}:1` : 'N/A'}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            )}

        </main>
    )
}
