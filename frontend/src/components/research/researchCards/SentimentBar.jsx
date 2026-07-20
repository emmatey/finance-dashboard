export default function SentimentBar({ score }) {
    if (score == null) return <p className="text-sm text-muted-foreground">No data available.</p>
    const position = Math.max(0, Math.min(100, ((score + 1) / 2) * 100))
    return (
        <div className="mt-2">
            <div
                className="relative h-2 rounded-full"
                style={{ background: 'linear-gradient(to right, var(--color-destructive), var(--color-border) 50%, var(--color-gain))' }}
            >
                <div
                    className="absolute top-[-4px] h-4 w-[3px] -translate-x-1/2 rounded-sm bg-foreground"
                    style={{ left: `${position}%` }}
                />
            </div>
            <div className="mt-1 flex justify-between text-xs text-muted-foreground">
                <span>Bearish</span>
                <span>Neutral</span>
                <span>Bullish</span>
            </div>
        </div>
    )
}
