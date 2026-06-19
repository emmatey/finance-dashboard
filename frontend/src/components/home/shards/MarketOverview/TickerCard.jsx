import { formatCurrencyUSD } from '../../../../scripts/utils';
import * as styles from './styles';

// One ticker packet rendered in its own small frame.
export default function TickerCard({ packet }) {
    const { ticker, company_name, current_price, pct_change } = packet;

    // pct_change arrives from the backend already as a percentage (e.g. -1.27),
    // so format it directly rather than treating it as a ratio.
    const pct = Number(pct_change);
    const isGain = pct >= 0;
    const pctSign = isGain ? '+' : '';

    return (
        <div style={styles.ticker}>
            <div style={styles.tickerSymbol}>{ticker}</div>
            <div style={styles.tickerName} title={company_name}>{company_name}</div>
            <div style={styles.tickerPrice}>{formatCurrencyUSD(current_price)}</div>
            <div style={styles.tickerPct(isGain)}>
                {pctSign}{pct.toFixed(2)}%
            </div>
        </div>
    );
}
