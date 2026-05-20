import { formatCurrencyUSD, formatPercent, formatNumber, formatLargeNumber } from '../../scripts/utils.js'

export default function FinancialMetricsCard({ metrics }) {
    return (
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
                                <div className="text-muted metric-label">{label}</div>
                                <div className="fw-semibold small">{value}</div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-muted small mb-0">Loading…</p>
                )}
            </div>
        </div>
    )
}
