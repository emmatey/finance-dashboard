// Shared lookup table, keyed by the same field names the API returns on
// summary/history rows (grand_total, cash_balance, portfolio_value).
//
// Split into its own file (instead of living in BalanceHistoryChart.jsx) because a
// component file can only export components under Vite's Fast Refresh rule
// (react-refresh/only-export-components) - otherwise this module can't hot-reload.
//
// Consumers:
// - BalanceHistoryChart.jsx: uses both `label` and `color` - colors feed
//   ChartContainer/Line stroke rendering, labels + colored dots render the
//   line-selector ToggleGroupItems.
// - AccountValueHeader.jsx: uses only `label`, to turn the active line's raw key
//   (e.g. "cash_balance") into human-readable text for the header description.
export const CHART_CONFIG = {
    grand_total: {
        label: "Account Value",
        color: "var(--chart-3)",
    },
    cash_balance: {
        label: "Cash Balance",
        color: "var(--chart-1)"
    },
    portfolio_value: {
        label: "Holdings Value",
        color: "var(--chart-2)",
    }
};
