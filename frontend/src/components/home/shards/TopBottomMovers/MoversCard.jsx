import { formatCurrencyUSD, formatPercent } from "@/scripts/utils"


export default function MoversCard({ data }) {
    return (
        <div>
            <div>
                <h3>{data.symbol}</h3>
                <small>{data.name}</small>
            </div>
            <div>
                <span>{formatCurrencyUSD(data.gain_loss)} {formatPercent(data.gain_loss_pct/100)}</span>
            </div>
            <div>
                <span>{formatCurrencyUSD(data.unit_price)}</span>
            </div>
        </div>
    )
}