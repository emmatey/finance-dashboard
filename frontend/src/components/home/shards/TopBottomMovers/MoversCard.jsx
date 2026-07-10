import { Link } from "react-router-dom"
import { formatCurrencyUSD, formatPercent } from "@/scripts/utils"


export default function MoversCard({ data }) {
    return (
        <div className="grid grid-cols-[2fr_1.5fr_1fr] items-center gap-4 px-2 py-1.5">
            <div>
                <h3>
                    <Link to={`/research?ticker=${data.symbol}`} className="text-foreground underline underline-offset-4 hover:text-blue-600 dark:hover:text-blue-400">
                        {data.symbol}
                    </Link>
                </h3>
                <small>{data.name}</small>
            </div>
            <span className={Number(data.todays_gain_loss_pct) > 0 ? 'text-right text-gain whitespace-nowrap' : 'text-right text-destructive whitespace-nowrap'}>
                {formatCurrencyUSD(data.todays_gain_loss)} ({formatPercent(data.todays_gain_loss_pct/100)})
            </span>
            <span className="text-right">{formatCurrencyUSD(data.unit_price)}</span>
        </div>
    )
}