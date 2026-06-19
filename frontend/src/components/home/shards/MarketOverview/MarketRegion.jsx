import TickerCard from './TickerCard';
import * as styles from './styles';

// One regional container: an abbreviation frame followed by a card per ticker.
export default function MarketRegion({ region, packets }) {
    return (
        <div style={styles.region}>
            <div style={styles.regionLabel}>{region}</div>
            {packets.map((packet) => (
                <TickerCard key={packet.ticker} packet={packet} />
            ))}
        </div>
    );
}
