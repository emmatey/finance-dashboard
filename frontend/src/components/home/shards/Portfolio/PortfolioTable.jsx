

const columnDef = [
    {
        accessorKey: "ticker_plus_name",
        header: "Symbol",
    },
    {
        accessorKey: "unit_price",
        header: "Last Price",
    },
    {
        accessorKey: "todays_gain_loss_plus_pct",
        header: "Today's gain/loss",
    },
    {
        accessorKey: "total_gain_loss_plus_pct",
        header: "Total gain/loss",
    },
    {
        accessorKey: "current_value",
        header: "Current Value",
    },
    {
        accessorKey: "",
        header: "% of account",
    },
    {
        accessorKey: "",
        header: "Quantity",
    },
    {
        accessorKey: "",
        header: "Cost Basis"
    }
];

export default function PortfolioTable({ data }) {
    // Combining 'ticker' and 'company name' to be displayed in one cell.
    const displayData = structuredClone(data);
    const portfolioVale = 
    if (displayData) {
        displayData.map((holding) => {
            holding['ticker_plus_name'] = [holding.symbol, holding.name]
            holding['todays_gain_loss_plus_pct'] = [holding.todays_gain_loss, holding.todays_gain_loss_pct]
            holding['total_gain_loss_plus_pct'] = [holding.gain_loss, holding.gain_loss_pct]
        })
    };

    console.log(displayData);

    return (
        <div>

        </div>
    )
}