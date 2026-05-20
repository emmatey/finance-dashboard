import '../styles/colors.css'

export default function SentimentBar({ score }) {
    if (score == null) return <p className="text-muted small mb-0">No data available.</p>
    const position = Math.max(0, Math.min(100, ((score + 1) / 2) * 100))
    return (
        <div className="mt-2">
            <div style={{
                position: 'relative',
                height: '8px',
                borderRadius: '4px',
                background: 'linear-gradient(to right, var(--color-loss), var(--color-border) 50%, var(--color-gain))'
            }}>
                <div style={{
                    position: 'absolute',
                    left: `${position}%`,
                    top: '-4px',
                    transform: 'translateX(-50%)',
                    width: '3px',
                    height: '16px',
                    background: '#333',
                    borderRadius: '2px'
                }} />
            </div>
            <div className="d-flex justify-content-between mt-1 small">
                <span className="text-muted">Bearish</span>
                <span className="text-muted">Neutral</span>
                <span className="text-muted">Bullish</span>
            </div>
        </div>
    )
}
