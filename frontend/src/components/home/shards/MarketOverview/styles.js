// Inline style objects for the market overview bar.
// Colors are pulled from colors.css custom properties via var(--...).

export const bar = {
    display: 'flex',
    flexDirection: 'row',
    gap: '0.75rem',
    overflowX: 'auto',
    padding: '0.75rem',
    background: 'var(--color-surface)',
    border: '1px solid var(--color-border)',
    borderRadius: '8px',
};

export const region = {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'stretch',
    gap: '0.5rem',
    flex: '0 0 auto',
    padding: '0.5rem',
    background: 'var(--color-bg)',
    border: '1px solid var(--color-border-subtle)',
    borderRadius: '6px',
};

// First frame of each region: the abbreviation (USA, EU, ...).
export const regionLabel = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flex: '0 0 auto',
    minWidth: '3rem',
    padding: '0 0.75rem',
    fontWeight: 700,
    color: 'var(--color-text-on-primary)',
    background: 'var(--color-primary)',
    borderRadius: '4px',
};

export const ticker = {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.15rem',
    flex: '0 0 auto',
    minWidth: '8rem',
    padding: '0.5rem 0.75rem',
    background: 'var(--color-surface-raised)',
    border: '1px solid var(--color-border)',
    borderRadius: '4px',
};

export const tickerSymbol = {
    fontWeight: 700,
    color: 'var(--color-primary)',
};

export const tickerName = {
    fontSize: '0.7rem',
    color: 'var(--color-link)',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    maxWidth: '8rem',
};

export const tickerPrice = {
    fontVariantNumeric: 'tabular-nums',
    color: 'var(--color-primary)',
};

// pct cell color depends on gain vs. loss.
export const tickerPct = (isGain) => ({
    fontVariantNumeric: 'tabular-nums',
    fontWeight: 600,
    color: isGain ? 'var(--color-gain)' : 'var(--color-loss)',
});

// Empty placeholder block used by the loading/empty skeleton.
export const skeletonBlock = {
    background: 'var(--color-border)',
    borderRadius: '3px',
    minHeight: '0.8rem',
    minWidth: '4rem',
};
