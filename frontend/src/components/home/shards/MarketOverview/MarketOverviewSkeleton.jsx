import * as styles from './styles';

// Empty, unlabeled frames that hold the bar's shape while data loads or when
// the fetch returns nothing (e.g. API down).
export default function MarketOverviewSkeleton() {
    const PLACEHOLDER_REGIONS = 5;
    const PLACEHOLDER_TICKERS = 2;

    return (
        <div style={styles.bar} aria-hidden="true">
            {Array.from({ length: PLACEHOLDER_REGIONS }).map((_, regionIdx) => (
                <div style={styles.region} key={regionIdx}>
                    <div style={{ ...styles.regionLabel, ...styles.skeletonBlock }} />
                    {Array.from({ length: PLACEHOLDER_TICKERS }).map((_, tickerIdx) => (
                        <div style={styles.ticker} key={tickerIdx}>
                            <div style={styles.skeletonBlock} />
                            <div style={styles.skeletonBlock} />
                            <div style={styles.skeletonBlock} />
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
}
