import { useEffect, useRef, useState } from 'react'
import { unpackResponse } from '../scripts/backend-fetch.js'

const RANGES = { '1yr': 31536000, '1mo': 2592000, '1wk': 604800 }

function usd(n) {
    if (n == null) return 'N/A'
    return Number(n).toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}

function pct(n) {
    if (n == null) return 'N/A'
    return (Number(n) * 100).toFixed(2) + '%'
}

function fmt(n, decimals = 2) {
    if (n == null) return 'N/A'
    return Number(n).toLocaleString('en-US', { maximumFractionDigits: decimals })
}

function fmtLarge(n) {
    if (n == null) return 'N/A'
    const abs = Math.abs(n)
    if (abs >= 1e12) return (n / 1e12).toFixed(2) + 'T'
    if (abs >= 1e9) return (n / 1e9).toFixed(2) + 'B'
    if (abs >= 1e6) return (n / 1e6).toFixed(2) + 'M'
    return Number(n).toLocaleString('en-US')
}

function formatRating(rating) {
    if (!rating) return 'N/A'
    return rating
        .replace(/_/g, ' ')
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .replace(/\b\w/g, c => c.toUpperCase())
}

function ratingColor(rating) {
    if (!rating) return ''
    const r = rating.toLowerCase()
    if (r.includes('buy')) return 'text-success'
    if (r.includes('sell') || r.includes('underperform')) return 'text-danger'
    return 'text-warning'
}

function sentimentLabel(score) {
    if (score == null) return 'No Data'
    if (score > 0.5) return 'Strongly Bullish'
    if (score > 0.15) return 'Bullish'
    if (score > -0.15) return 'Neutral'
    if (score > -0.5) return 'Bearish'
    return 'Strongly Bearish'
}

function sentimentColorClass(score) {
    if (score == null) return 'text-muted'
    if (score > 0.15) return 'text-success'
    if (score < -0.15) return 'text-danger'
    return 'text-warning'
}

function SentimentBar({ score }) {
    if (score == null) return <p className="text-muted small mb-0">No data available.</p>
    const position = Math.max(0, Math.min(100, ((score + 1) / 2) * 100))
    return (
        <div className="mt-2">
            <div style={{ position: 'relative', height: '8px', borderRadius: '4px', background: 'linear-gradient(to right, #FF534C, #dee2e6 50%, #16A34A)' }}>
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
            <div className="d-flex justify-content-between mt-1" style={{ fontSize: '0.7rem' }}>
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
                const local = await unpackResponse(localRes)
                if (!cancelled) setData(local)
            } catch {
                // ticker may not be in DB yet — continue to online
            }

            try {
                const onlineRes = await fetch(`/api/research/online?ticker=${ticker}`)
                const online = await unpackResponse(onlineRes)
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
                        <span className="fw-bold fs-3">{lastPrice != null ? usd(lastPrice) : '—'}</span>
                        {metrics && (
                            <span className="text-muted small">
                                Open {usd(metrics.market_open)}
                                <span className="mx-2">·</span>
                                Prev Close {usd(metrics.prev_close)}
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
                                    <p className="small" style={{ maxHeight: '170px', overflowY: 'auto' }}>{profile.company_desc ?? 'No description available.'}</p>
                                    <table className="table table-sm mb-0">
                                        <tbody>
                                            {[
                                                ['Sector', profile.sector],
                                                ['Industry', profile.industry],
                                                ['Employees', profile.employee_count != null ? fmt(profile.employee_count, 0) : null],
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
                                        ['Market Cap', fmtLarge(metrics.market_cap)],
                                        ['EPS', usd(metrics.eps)],
                                        ['Beta', fmt(metrics.beta)],
                                        ['Trailing P/E', fmt(metrics.trailing_pe)],
                                        ['Forward P/E', fmt(metrics.forward_pe)],
                                        ['Profit Margin', pct(metrics.profit_margin)],
                                        ['Dividend Yield', pct(metrics.dividend_yield)],
                                        ['52-wk High', usd(metrics.fifty_two_week_high)],
                                        ['52-wk Low', usd(metrics.fifty_two_week_low)],
                                        ['50-day Avg', usd(metrics.fifty_day_average)],
                                        ['200-day Avg', usd(metrics.two_hundred_day_average)],
                                        ['Price / Book', fmt(metrics.price_to_book)],
                                        ['Book Value', usd(metrics.book_value)],
                                        ['Shares Out.', fmtLarge(metrics.shares_outstanding)],
                                        ['Current Ratio', fmt(metrics.current_ratio)],
                                        ['Debt / Equity', fmt(metrics.debt_to_equity)],
                                        ["Today's Vol.", fmtLarge(metrics.todays_volume)],
                                        ['10-day Avg Vol', fmtLarge(metrics.ten_day_avg_volume)],
                                        ['3-mo Avg Vol', fmtLarge(metrics.three_month_avg_volume)],
                                    ].map(([label, value]) => (
                                        <div key={label} className="col border-bottom pb-1">
                                            <div className="text-muted" style={{ fontSize: '0.72rem' }}>{label}</div>
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
                                        <span className={`fw-bold fs-4 ${ratingColor(metrics.rating)}`}>
                                            {formatRating(metrics.rating)}
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
                                                <td className="small">{usd(metrics.target_price)}</td>
                                            </tr>
                                            <tr>
                                                <th className="text-muted fw-normal small">Current Price</th>
                                                <td className="small">{usd(lastPrice)}</td>
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
                                        <span className={`fw-bold fs-4 ${sentimentColorClass(metrics.insider_sentiment)}`}>
                                            {sentimentLabel(metrics.insider_sentiment)}
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
                                <ul className="list-unstyled mb-0" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                                    {news.map((n, i) => (
                                        <li key={n.uuid ?? i} className="d-flex gap-2 align-items-start py-2 border-bottom">
                                            {n.thumbnail && (
                                                <img src={n.thumbnail} alt="" style={{ width: '64px', height: '42px', objectFit: 'cover', borderRadius: '4px', flexShrink: 0 }} />
                                            )}
                                            <div>
                                                <a href={n.link} target="_blank" rel="noreferrer" className="fw-semibold small d-block mb-1">
                                                    {n.title}
                                                </a>
                                                <span className="text-muted" style={{ fontSize: '0.75rem' }}>
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
                                <div className="table-responsive" style={{ maxHeight: '400px', overflowY: 'auto' }}>
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
                                                    <td className="small">{t.shares != null ? fmt(t.shares, 0) : 'N/A'}</td>
                                                    <td className="small">{usd(t.transaction_value)}</td>
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
