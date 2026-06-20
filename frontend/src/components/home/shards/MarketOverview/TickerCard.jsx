import { formatCurrencyUSD } from '../../../../scripts/utils';

export default function TickerCard({ packet }) {
    const { ticker, company_name, current_price, pct_change } = packet;
    const pct = Number(pct_change);
    const pctSign = pct >= 0 ? '+' : '';

    return (
        <li>
            <strong>{ticker}</strong> — {company_name} — {formatCurrencyUSD(current_price)} — {pctSign}{pct.toFixed(2)}%
        </li>
    );
}
